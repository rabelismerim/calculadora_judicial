from base.claim.models import Claim
from calculation.comparative.models import Comparative
from calculation.criterion.models import Criterion
from calculation.funds.views import CreateFunds
from calculation.models import Calculation
from calculation.schemas import CalculationSchema
from calculation.verdict.models import TypeCalculation, Verdict
from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission


class AbstractCalculationApi(AbstractViewApi):
    """This class provides basic HTTP methods for managing Calculation Objects. 
    It includes a serializer_class and required permission_classes to authenticate the users, 
    a model instance with a corresponding schema as well as custom query parameters to retrieve data.
    """
    serializer_class = CalculationSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Calculation
    schema = AutoSchema(tags=["Calculation"])

    query_params = [
        {
            "name": "nome",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": "Nome do advogado",
            "schema": {"type": "string"}
        }
    ]


class CalculationDetailApi(AbstractCalculationApi):
    """A class for handling detail HTTP requests for a Calculation object
    HTTP methods for retrieving particular Calculation detail"""
    http_method_names = ['get']


class CalculationApi(AbstractCalculationApi):
    """HTTP methods for Calculation"""
    http_method_names = ['post', 'get']

    def post(self, request, *args, **kwargs):
        """
        Creates a new instance of the Calculation model, receiving a dictionary as an argument and returning details of the newly created instance. 
        Before creation of the Calculation instance, it will create related Criterion and Verdict instances based on the input data. 
        Furthermore, if any Funds objects are found in the input data, it will also iteratively call the CreateFunds helper class to create the necessary
        Funds instances related to the Calculation. Finally, a JsonResponse with the serialized Calculation instance is returned upon successful completion.

        Arguments
        request -- Containing the input data, a Request object that supports .data attribute access.
        args -- Additional positional arguments, if given.
        kwargs -- Additional keyword arguments, if given.

        Returns
        A JsonResponse containing the serialized Calculation instance.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_calculation = serializer.validated_data
        new_verdicts = new_calculation.pop('verdict', None)
        new_funds = new_calculation.pop('funds', None)
        calculation = self.model.objects.create(**new_calculation)
        creditor = calculation.creditor
        clain_creditor = creditor.get_clain_creditor()
        clain_lawyer = creditor.get_clain_lawyer()
        new_criterion = {
            'calculation': calculation,
            'rate': creditor.rate,
            'admission': creditor.admission,
            'dismissal': creditor.dismissal,
            'default_interest': creditor.default_interest,
            'fine': creditor.fine,
            'advocative_hours': creditor.advocative_hours,
        }

        if clain_creditor:
            new_criterion['claim_credor'] = Claim.objects.create(
                classes=clain_creditor.classes, coins=clain_creditor.coins, archive_json=clain_creditor.archive_json)

        if clain_lawyer:
            new_criterion['claim_lawyer'] = Claim.objects.create(
                classes=clain_lawyer.classes, coins=clain_lawyer.coins, archive_json=clain_lawyer.archive_json)

        Criterion.objects.create(**new_criterion)

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
            Comparative.objects.create(calculation=calculation)
        return JsonResponse({'calculation': self.serializer_class(calculation, many=False).data}, status=status.HTTP_201_CREATED)
