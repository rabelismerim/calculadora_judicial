from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from creditors.recovering.models import Recovering
from creditors.recovering.schemas import RecoveringSchema


class RecoveringApi(AbstractViewApi):
    """HTTP methods for Recovering"""
    http_method_names = ['post', 'get']
    serializer_class = RecoveringSchema
    permission_classes = [permissions.IsAdminUser]
    model = Recovering
    schema = AutoSchema(tags=["Creditors - Recovering"])

    query_params = [
        {
            "name": "registration",
            "field": "registration__icontains",
            "in": "query",
            "required": False,
            "description": "Registro",
            "schema": {"type": "string"}
        }
    ]

    def post(self, request, *args, **kwargs):
        """
           Create Recovering receiving a dict, return Recovering detail
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_recovering = serializer.validated_data
        recovering = self.model.objects.create(**new_recovering)
        recovering.save()
        return JsonResponse({'recovering': self.serializer_class(recovering, many=False).data}, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """Get Recovering details"""
        recoverings = self.get_query()
        return JsonResponse({'recoverings': recoverings})
