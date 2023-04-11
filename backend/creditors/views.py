from django.db import transaction

from base.claim.models import ClaimCreditor, ClaimLawyer
from base.coins.models import Coins
from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.entity.models import Entity
from core.permission.views import CheckHasPermission
from creditors.notice.models import Notice, NoticeRecovering
from creditors.schemas import CreditorCreateSchema, CreditorSchema, CreditorUpdateSchema
from creditors.models import Creditor
from utils import get_user_model

User = get_user_model()


class AbstractCreditorApi(AbstractViewApi):
    """HTTP methods for creditor"""
    serializer_class = CreditorSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Creditor
    schema = AutoSchema(tags=["Creditor"])

    query_params = [
        {
            "name": "descrição",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": "Descrição do projeto",
            "schema": {"type": "string"}
        }
    ]

    def get_queryset(self):
        return {'recovering__project__engagement__users__user': self.request.user}


class CreditorDetailApi(AbstractCreditorApi):
    """HTTP methods for creditor Detail"""
    http_method_names = ['get', ]


class CreditorCreateApi(AbstractCreditorApi):
    """HTTP methods for Project Create"""
    http_method_names = ['get']
    serializer_class = CreditorCreateSchema

    query_params = []

    def get(self, request, *args, **kwargs):
        """Abstract method for default get model. Overide method in class for custom operation"""
        data = {}
        for key, field in self.serializer_class(many=False).fields.items():
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

    def get(self, request, *args, **kwargs):
        """
        Retrieves a queryset of creditors related to a given project ID,
        serializes it and returns a JSON response with the serialized data.

        Returns
        -------
        JsonResponse
            A response with a JSON object containing a list of serialized creditor data.
        """
        project_id = kwargs.get('id')
        creditors = self.serializer_class(self.model.objects.filter(recovering__project_id=project_id), many=True).data
        return JsonResponse({'creditors': creditors})


class CreditorApi(AbstractCreditorApi):
    """ AbstractCreditorApi's HTTP methods for creating new creditor with required fields."""
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        """
        Create creditor by receiving a dictionary object with required fields.
        Creditor detail will be returned upon successful completion of operation
        """
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


class CreditorUpdateApi(AbstractCreditorApi):
    """HTTP methods for update creditor"""
    http_method_names = ['put']
    serializer_class = CreditorUpdateSchema
