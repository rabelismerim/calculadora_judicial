from base.claim.models import Claim
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


class CalculationApi(AbstractViewApi):
    """HTTP methods for Calculation"""
    http_method_names = ['post', 'get']
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

    def post(self, request, *args, **kwargs):
        """
           Create Calculation receiving a dict, return Calculation detail
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
        return JsonResponse({'calculation': self.serializer_class(calculation, many=False).data}, status=status.HTTP_201_CREATED)
