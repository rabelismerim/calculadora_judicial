from django.db import transaction
from rest_framework.generics import get_object_or_404

from base.claim.models import ClaimCreditor, ClaimLawyer
from base.coins.models import Coins
from calculation.models import Calculation
from calculation.schemas import ValidatedIDSchema
from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status, serializers

from rest_framework import permissions
from core.entity.models import Entity
from core.entity.schemas import EntityCheckSchema
from core.permission.views import CheckHasPermission, check_query_permission
from creditors.notice.models import Notice, NoticeRecovering
from creditors.schemas import CreditorCreateSchema, CreditorSchema, CreditorUpdateSchema
from creditors.models import Creditor
from utils import get_user_model, _, doc

User = get_user_model()
docs = {
    'init': _("""The `Creditor` class represents a creditor of an entity in the context of a credit recovery process. 
    It stores relationship with the `Entity` model and with the `Recovering` model. In addition, it has a description 
    of the creditor stored in the `description` field.
    """)
}


class AbstractCreditorApi(AbstractViewApi):
    """HTTP methods for creditor"""
    serializer_class = CreditorSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Creditor
    docs = docs.copy()
    query_params = [
        {
            "name": "description",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Description")),
            "schema": {"type": "string"}
        }
    ]
    perms = ['can_view_all_projects']

    @check_query_permission(perms)
    def get_queryset(self):
        return {'recovering__project__engagement__users__user': self.request.user}


class CreditorDetailApi(AbstractCreditorApi):
    """HTTP methods for creditor Detail"""
    http_method_names = ['get', ]
    init_docs = docs.copy()
    docs_get = {
        'get': _("""Retrieve a creditor by their given ID,
        serializes it and returns a JSON response with the serialized data.

        Returns
        -------
        JsonResponse
            A response with a JSON object containing a serialized creditor data object.""")
    }
    init_docs.update(docs_get)
    docs = init_docs


class CreditorCreateApi(AbstractCreditorApi):
    """HTTP methods for CreditorCreate options"""
    http_method_names = ['get']
    serializer_class = CreditorCreateSchema
    docs = docs.copy()
    query_params = [
        {
            "name": "option",
            "field": "option",
            "in": "query",
            "required": False,
            "description": str(_("Option")),
            "schema": {"type": "string"}
        }
    ]

    @doc(_("""Choice options for the various Choices that exist on the platform. It can be filtered by the desired 
    option. Contain the `ID` and the `caption`, where the ID refers to the value that must be passed, and the caption 
    what must be displayed to the user"""))
    def get(self, request, *args, **kwargs):
        data = {}
        option = self.get_query_parameters().get('option')
        for key, field in self.serializer_class(many=False).fields.items():
            if option:
                if option in key:
                    data[key] = list(field.data)
            else:
                data[key] = list(field.data)
        return JsonResponse({'options': data}, status=status.HTTP_200_OK)


class CreditorListApi(AbstractCreditorApi):
    """
    A view for retrieving a list of creditors from a specific project.
    Inherits from AbstractCreditorApi.

    Methods
    -------
    get(self, request, *args, **kwargs):
        Retrieves a queryset of creditors related to a given project ID,
        serializes it using self.serializer_class, and returns a JSON response
        with the serialized data.
    """
    http_method_names = ['get']
    docs = docs.copy()
    operation_id_base = 'CreditorList'

    @doc(_("""Retrieves a queryset of creditors related to a given project ID,
        serializes it and returns a JSON response with the serialized data.

        Returns
        -------
        JsonResponse
            A response with a JSON object containing a list of serialized creditor data.
        """))
    def get(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        creditors = self.serializer_class(self.model.objects.filter(
            recovering__project_id=project_id), many=True).data
        return JsonResponse({'creditors': creditors})


class CreditorApi(AbstractCreditorApi):
    """ AbstractCreditorApi's HTTP methods for creating new creditor with required fields."""
    http_method_names = ['post']
    docs = docs.copy()

    @doc(_("""Create creditor by receiving a dictionary object with required fields.
        Creditor detail will be returned upon successful completion of operation
        """))
    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = self.serializer_class(data=request.data)

            serializer.is_valid(raise_exception=True)
            creditor = serializer.validated_data

            entity = creditor.pop('entity')
            notices = creditor.pop('notice', [])
            notice_recoverings = creditor.pop('notice_recovering', [])
            claims_creditor = creditor.pop('claim_creditor', [])
            claim_lawyer = creditor.pop('claimlawyer', None)

            creditor['entity'], created = Entity.objects.get_or_create(defaults=entity,
                                                                       **{'legal_number': entity['legal_number']})

            new_creditor = self.model.objects.create(**creditor)

            if claims_creditor:
                for claim_creditor in claims_creditor:
                    coins = claim_creditor.get('coins')
                    claim_creditor['coins'] = Coins.objects.create(**coins)
                    claim_creditor['creditor'] = new_creditor
                    ClaimCreditor.objects.create(**claim_creditor)

            if claim_lawyer:
                coins = claim_lawyer.get('coins')
                claim_lawyer['coins'] = Coins.objects.create(**coins)
                claim_lawyer['creditor'] = new_creditor
                ClaimLawyer.objects.create(**claim_lawyer)

            if notices:
                for notice in notices:
                    coins = notice.get('coins')
                    notice['coins'] = Coins.objects.create(**coins)
                    notice['creditor'] = new_creditor
                    Notice.objects.create(**notice)

            if notice_recoverings:
                for notice_recovering in notice_recoverings:
                    coins = notice_recovering.get('coins')
                    notice_recovering['coins'] = Coins.objects.create(**coins)
                    notice_recovering['creditor'] = new_creditor
                    NoticeRecovering.objects.create(**notice_recovering)
        return JsonResponse({'creditor': self.serializer_class(new_creditor, many=False).data},
                            status=status.HTTP_201_CREATED)


class CreditorCheckApi(AbstractViewApi):
    """AbstractCreditorApi's HTTP methods for creating new creditor with required fields."""
    http_method_names = ['post']
    docs = docs.copy()
    model = Entity
    serializer_class = EntityCheckSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    tags = [_('Creditor')]
    operation_id_base = 'CreditorCheckLN'

    @doc(_("""Check the creditor to see if he exists in that recovering, based on his legal_number
        
        Returns
            an HTTP 200 if it does not exist, an exception is generated when it exists
        """))
    def post(self, request, *args, **kwargs):
        recovering_id = kwargs.get('recovering_id')
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        legal_number = serializer.validated_data.get('legal_number')
        if Creditor.objects.filter(entity__legal_number=legal_number, recovering_id=recovering_id).exists():
            raise serializers.ValidationError([_('Legal number already registered')])
        return JsonResponse({'message': 'Legal number unregistered'})


class CreditorUpdateApi(AbstractCreditorApi):
    """HTTP methods for update creditor"""
    http_method_names = ['put']
    serializer_class = CreditorUpdateSchema
    docs = docs.copy()
    docs['put'] = _("""Method to change creditor information instance.

            Receives and validates JSON data with the fields `description`, `admission`, `dismissal`, 
            `default_interest`, `fine` or `advocative_hours`.
            
            Finds the Calculation instance based on the URL parameter id.
            Returns a JSON response with the updated Creditor object.
            """)


class CalcValidateApi(AbstractViewApi):
    """
    API view to change validated calculations of a list of ids.

    Only authenticated users with permissions and access can change validated calculation.

    Allowed HTTP Method: POST

    URL query parameters: None

    Response status code:
    - 200 OK: Successfully updated the Calculation validate.
    """
    http_method_names = ['post']

    serializer_class = ValidatedIDSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    query_params = []
    model = Creditor
    docs = docs.copy()

    @doc(_("""POST to change valid calculations

    Receives a list of calculation ids.
    Finds the creditor instance based on the URL parameter ID.
    Return a 200 response if allowed.

    Invalidates all the calculations that are not in the received list, and validates only the calculations of the 
    received ids that are in the `Approved` step
    """))
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_calculation = serializer.validated_data
        creditor = get_object_or_404(self.model, id=kwargs.get('id'))
        calculations = new_calculation.pop('calculations', [])

        invalids, valids = creditor.validate_calcs(calculations)

        return JsonResponse({'invalids': invalids, 'valids': valids}, status=status.HTTP_200_OK)
