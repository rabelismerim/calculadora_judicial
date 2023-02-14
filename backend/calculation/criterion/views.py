from django.forms import model_to_dict
from base.claim.models import Claim
from calculation.criterion.models import Criterion
from calculation.criterion.schemas import CriterionSchema
from calculation.models import Calculation
from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission


class CriterionApi(AbstractViewApi):
    """HTTP methods for Criterion"""
    http_method_names = ['post', 'get']
    serializer_class = CriterionSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Criterion
    schema = AutoSchema(tags=["Criterion"])

    query_params = [
        {
            "name": "sentença",
            "field": "calculation__description__icontains",
            "in": "query",
            "required": False,
            "description": "Nome da Sentença",
            "schema": {"type": "string"}
        }
    ]

    def post(self, request, *args, **kwargs):
        """
           Create criterion receiving a dict, return criterion detail
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        criterion = serializer.validated_data
        calculation = Calculation.objects.filter(
            id=criterion.get('calculation_id')).first()
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

        criterion = self.model.objects.create(**new_criterion)
        return JsonResponse({'criterion': self.serializer_class(criterion, many=False).data}, status=status.HTTP_201_CREATED)
