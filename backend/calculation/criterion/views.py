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
    http_method_names = ['get']
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
