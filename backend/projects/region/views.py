from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from projects.region.models import Region
from projects.region.schemas import RegionSchema 


class RegionApi(AbstractViewApi):
    """HTTP methods for Region"""
    http_method_names = ['post', 'get']
    serializer_class = RegionSchema
    permission_classes = [permissions.IsAdminUser]
    model = Region
    schema = AutoSchema(tags=["Region - Comarca"])

    query_params = [
        {
            "name": "nome",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": "Nome da Comarca",
            "schema": {"type": "string"}
        }
    ]
    
    def post(self, request, *args, **kwargs):
        """
           Create Region receiving a dict, return Region detail
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_region = serializer.validated_data
        region = self.model.objects.create(**new_region)
        region.save()
        return JsonResponse({'region': self.serializer_class(region, many=False).data}, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """Get Regions details"""
        regions = self.get_query()
        return JsonResponse({'regions': regions})