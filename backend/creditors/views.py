from base.claim.models import ClaimCreditor, ClaimLawyer
from base.coins.models import Coins
from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.entity.models import Entity
from core.permission.views import CheckHasPermission
from creditors.notice.models import Notice
from creditors.schemas import CreditorCreateSchema, CreditorSchema
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


class CreditorApi(AbstractCreditorApi):
    """HTTP methods for creditor"""
    http_method_names = ['get', 'post']

    def post(self, request, *args, **kwargs):
        """
           Create creditor receiving a dict, return creditor detail
        """
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)
        creditor = serializer.validated_data

        entity = creditor.pop('entity')
        notice = creditor.pop('notice', None)
        claim_creditor = creditor.pop('claimcreditor', None)
        claim_lawyer = creditor.pop('claimlawyer', None)

        creditor['entity'] = Entity.objects.create(**entity)

        new_creditor = self.model.objects.create(**creditor)

        if claim_creditor:
            coins = claim_creditor.get('coins')
            claim_creditor['coins'] = Coins.objects.create(**coins)
            claim_creditor['creditor'] = new_creditor
            ClaimCreditor.objects.create(**claim_creditor)

        if claim_lawyer:
            coins = claim_lawyer.get('coins')
            claim_lawyer['coins'] = Coins.objects.create(**coins)
            claim_lawyer['creditor'] = new_creditor
            ClaimLawyer.objects.create(**claim_lawyer)

        if notice:
            coins = notice.get('coins')
            notice['coins'] = Coins.objects.create(**coins)
            notice['creditor'] = new_creditor
            Notice.objects.create(**notice)
        return JsonResponse({'creditor': self.serializer_class(new_creditor, many=False).data},
                            status=status.HTTP_201_CREATED)
