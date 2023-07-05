import json

from django.db import transaction
from base.claim.models import Claim
from calculation.comment.models import Comment, StepComment
from calculation.comparative.models import Comparative
from calculation.criterion.models import Criterion, CriterionClaimCredor
from calculation.funds.views import CreateFunds
from calculation.models import Calculation, Incident
from calculation.premise.views import PremiseCreator
from calculation.schemas import CalculationSchema, IncidentSchema, ChangeStepSerializer, CalculationV2Schema, \
    CalculationAllFundsSchema, CheckStepSerializer
from calculation.verdict.models import TypeCalculation, Verdict
from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status, serializers
from rest_framework import permissions
from core.permission.views import CheckHasPermission, CanChangeStep
from creditors.models import Creditor
from utils import _, doc

docs = {
    'init': _("""Represents all the calculation information. It gathers all the information relevant to the process.
     It gathers the information of `extract`, `appropriations`, `assumptions`, claims, `comparative`, `sentences`,
    `editais` and the `status of the calculation`.
    """),
}


class AbstractCalculationApi(AbstractViewApi):
    """This class provides basic HTTP methods for managing Calculation Objects.
    It includes a serializer_class and required permission_classes to authenticate the users,
    a model instance with a corresponding schema as well as custom query parameters to retrieve data.
    """
    serializer_class = CalculationSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Calculation

    query_params = [
        {
            "name": "number",
            "field": "incident__number__icontains",
            "in": "query",
            "required": False,
            "description": _("Incident number"),
            "schema": {"type": "string"}
        }
    ]
    docs = docs.copy()


class IncidentApi(AbstractViewApi):
    """This class provides basic HTTP methods for managing Incident Objects.
    It includes a serializer_class and required permission_classes to authenticate the users,
    a model instance with a corresponding schema as well as custom query parameters to retrieve data.
    """
    serializer_class = IncidentSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Incident
    http_method_names = ['post', 'get']
    query_params = [
        {
            "name": "number",
            "field": "incident__number__icontains",
            "in": "query",
            "required": False,
            "description": _("Incident number"),
            "schema": {"type": "string"}
        }
    ]
    docs = {
        'init': _("""Represents the `incident number` related to the process. Within a process there can be several
        `numbers of incidents`, and when doing the calculation, it is necessary to pass which number is related.
            """),
        'post': _("""Create Incident object from request data and return Incident detail.
            Returns:
                JsonResponse: A JSON response containing the created Funds
                 object detail.

            Raises:
                serializers.ValidationError: If the input data is invalid.
                """)
    }


class CalculationDetailApi(AbstractCalculationApi):  # V1
    """A class for handling detail HTTP requests for a Calculation object
    HTTP methods for retrieving particular Calculation detail"""
    http_method_names = ['get']
    docs = docs.copy()

    docs['get'] = _("""This method handles GET requests for the view. It retrieves a specific Calculation using the
    given id from the query parameters and serializes the result into JSON format before returning it as
                 an HTTP response.

                    Returns:
                        JsonResponse: An HTTP response containing the serialized Calculation data retrieved.
                    """)


class CalculationDetailV2Api(AbstractCalculationApi):  # V2
    """A class for handling detail HTTP requests for a Calculation object
    HTTP methods for retrieving particular Calculation detail"""
    http_method_names = ['get']
    docs = docs.copy()
    serializer_class = CalculationV2Schema
    allowed_versions = ['v1', 'v2']

    docs['get'] = _("""This method handles GET requests for the view. It retrieves a specific Calculation using the
    given id from the query parameters and serializes the result into JSON format before returning it as
                 an HTTP response.

                    Returns:
                        JsonResponse: An HTTP response containing the serialized Calculation data retrieved.
                    """)


class CalculationListApi(AbstractCalculationApi):
    """HTTP methods for Calculation"""
    http_method_names = ['get']
    docs = docs.copy()
    operation_id_base = 'CreditorListCalculation'

    @doc(_("""This method handles GET requests for the view. It retrieves a list of objects Calculation using the given
                creditor_id from the query parameters and serializes the result into JSON format before returning it as
                 anHTTP response.

                    Returns:
                        JsonResponse: An HTTP response containing the serialized Calculation data retrieved.
                    """))
    def get(self, request, *args, **kwargs):
        creditor_id = kwargs.get('creditor_id')
        statement = self.model.objects.filter(creditor_id=creditor_id)
        statement_data = self.serializer_class(statement, many=True).data
        return JsonResponse({'calculations': statement_data})


class CalculationAllFundsDetailApi(AbstractCalculationApi):
    """HTTP methods for Calculation"""
    http_method_names = ['get']
    docs = docs.copy()
    serializer_class = CalculationAllFundsSchema
    operation_id_base = 'CalculationAllFunds'

    docs['get'] = _("""This method handles GET requests for the view. It retrieves a list of all funds Calculation 
    using the given id from the query parameters and serializes the result into JSON format before returning it as 
    an HTTP response.

    Returns:
        JsonResponse: An HTTP response containing the serialized Calculation data retrieved.
    """)


class CalculationApi(AbstractCalculationApi):
    """HTTP methods for Calculation"""
    http_method_names = ['post']
    docs = docs.copy()

    @doc(_("""Creates a new instance of the Calculation model, receiving a dictionary as an argument and returning details
         of the newly created instance.
        Before creation of the Calculation instance, it will create related Criterion and Verdict instances based on
        the input data.
        Furthermore, if any Funds objects are found in the input data, it will also iteratively call the CreateFunds
         helper class to create the necessary
        Funds instances related to the Calculation. Finally, a JsonResponse with the serialized Calculation instance
         is returned upon successful completion.


        Returns
        A JsonResponse containing the serialized Calculation instance.
        """))
    def post(self, request, *args, **kwargs):  # Generate calculation
        with transaction.atomic():

            # get_calculation_impediment_list
            serializer = self.serializer_class(data=request.data)

            serializer.is_valid(raise_exception=True)
            new_calculation = serializer.validated_data

            # TODO: descomentar apos testes e implementacao de edicao no front end
            # creditor = Creditor.objects.filter(id=new_calculation['creditor_id']).first()
            # impediment_list = creditor.get_calculation_impediment_list()
            # if impediment_list:
            #     raise serializers.ValidationError(impediment_list)

            new_verdicts = new_calculation.pop('verdict', None)
            new_funds = new_calculation.pop('funds', None)

            # coins = new_calculation.get('coins')
            # new_calculation['coins'] = Coins.objects.create(**coins)

            calculation = self.model.objects.create(**new_calculation)
            creditor = calculation.creditor
            project = creditor.recovering.project
            claims_creditor = creditor.get_claims_creditor()
            claim_lawyer = creditor.get_claim_lawyer()

            new_criterion = {
                'calculation': calculation,
                'rate': creditor.rate,
                'admission': creditor.admission,
                'dismissal': creditor.dismissal,
                'default_interest': creditor.default_interest,
                'fine': creditor.fine,
                'advocative_hours': creditor.advocative_hours,
                'occurrence': creditor.occurrence,
                'representation_documentation': creditor.representation_documentation,
                'claim_type': creditor.claim_type,
                'physical_person': creditor.physical_person,
                'date_rj_request': project.date_rj_request,
                'date_rj_filing': project.date_rj_filing,
                'date_citation': project.date_citation,
            }

            nature_ids = creditor.nature.all().values_list('id', flat=True)

            if claim_lawyer:
                new_criterion['claim_lawyer'] = Claim.objects.create(
                    classes=claim_lawyer.classes, coins=claim_lawyer.coins, archive_json=claim_lawyer.archive_json)

            criterion = Criterion.objects.create(**new_criterion)
            criterion.nature.add(*nature_ids)
            criterion.save()

            if claims_creditor:
                for claim_creditor in claims_creditor:
                    new_claim = Claim.objects.create(
                        classes=claim_creditor.classes, coins=claim_creditor.coins,
                        archive_json=claim_creditor.archive_json)
                    CriterionClaimCredor.objects.create(claim_creditor=new_claim, criterion=criterion)
            if new_verdicts:
                for new_verdict in new_verdicts:
                    new_verdict['calculation'] = calculation
                    type_calculation = new_verdict.pop('type_calculation')
                    new_verdict['type_calculation'] = TypeCalculation.objects.create(
                        **type_calculation)
                    Verdict.objects.create(**new_verdict)
            if new_funds:
                for fund in new_funds:
                    CreateFunds(fund, calculation.id).create_funds()

            # TODO: change creation Comparative to Generate Calculation finish
            if Comparative.objects.filter(calculation=calculation).exists() is False:
                comparative = Comparative()
                comparative.calculation = calculation
                comparative.save()
                comparative.checks()

            PremiseCreator(calculation)
        return JsonResponse({'calculation': self.serializer_class(calculation, many=False).data},
                            status=status.HTTP_201_CREATED)


class ChangeStepApi(AbstractViewApi):
    """
    API view to change the step of a Calculation model instance.

    Only authenticated users with permissions and access to the Calculation can change the step.

    Allowed HTTP Method: PUT

    Required data to be sent in the request body:
    - next_step (string): The next step to be set.

    URL query parameters: None

    Response data format:
    - calculation (object): Serialized Calculation object with the updated step.

    Response status code:
    - 200 OK: Successfully updated the Calculation step.
    """
    http_method_names = ['put']

    serializer_class = ChangeStepSerializer
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission, CanChangeStep]

    model = Calculation
    docs = docs.copy()

    @doc(_("""PUT method to change the step of the Calculation instance.

        Receives and validates JSON data with the next_step string.
        Finds the Calculation instance based on the URL parameter id.
        Optional field `comments`, a list of objects containing the text field
        Returns a JSON response with the updated Calculation object.

        Possible status are `To Calculate`, `To Review`, `To Approve`, `To Approve Special`, `Failed`, `Approved`,
        """))
    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_calculation = serializer.validated_data
        comments = new_calculation.pop('comments', [])
        special_approvers = new_calculation.pop('special_approvers', [])
        calculation_id = kwargs.get('id', None)
        calculation = self.model.objects.filter(id=calculation_id).first()

        with transaction.atomic():
            calculation.set_step_by_char(new_calculation['next_step'], user=request.user,
                                         special_approvers=special_approvers)
            calc_comment = StepComment.objects.create(calculation=calculation, step=calculation.step)
            for comment in comments:
                new_comment = Comment.objects.create(**comment)
                calc_comment.comments.add(new_comment.id)
            calc_comment.save()
        return JsonResponse({'calculation': CalculationSchema(calculation, many=False).data}, status=status.HTTP_200_OK)


class CheckStepApi(AbstractViewApi):
    """
    API view to change the step of a Calculation model instance.

    Only authenticated users with permissions and access to the Calculation can change the step.

    Allowed HTTP Method: PUT

    Required data to be sent in the request body:
    - next_step (string): The next step to be set.

    URL query parameters: None

    Response data format:
    - calculation (object): Serialized Calculation object with the updated step.

    Response status code:
    - 200 OK: Successfully updated the Calculation step.
    """
    http_method_names = ['put']

    serializer_class = CheckStepSerializer
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission, CanChangeStep]

    model = Calculation
    docs = docs.copy()

    @doc(_("""PUT to check the step of the Calculation instance.

    Receive and validate JSON data with a next_step string.
    Finds the calculation instance based on the URL parameter ID.
    Returns a 200 response if allowed.
    
    Possible statuses are `To calculate`, `To review`, `To approve`, `To approve special`, `Failed`, `Approved`,
    """))
    def put(self, request, *args, **kwargs):
        return JsonResponse({}, status=status.HTTP_200_OK)
