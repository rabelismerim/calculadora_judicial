from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from projects.layer.models import Layer
from projects.layer.schemas import LayerSchema 


class LayerApi(AbstractViewApi):
    """HTTP methods for Layer"""
    http_method_names = ['post', 'get']
    serializer_class = LayerSchema
    permission_classes = [permissions.IsAdminUser]
    model = Layer
    schema = AutoSchema(tags=["Layer"])

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
           Create Layer receiving a dict, return Layer detail
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_layer = serializer.validated_data
        layer = self.model.objects.create(**new_layer)
        layer.save()
        return JsonResponse({'layer': self.serializer_class(layer, many=False).data}, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """Get layers details"""
        layers = self.get_query()
        return JsonResponse({'layers': layers})