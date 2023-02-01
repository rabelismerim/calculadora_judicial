from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from creditors.classes.models import Classes
from creditors.classes.schemas import ClassesSchema 


class ClassesApi(AbstractViewApi):
    """HTTP methods for Classes"""
    http_method_names = ['post', 'get']
    serializer_class = ClassesSchema
    permission_classes = [permissions.IsAdminUser]
    model = Classes
    schema = AutoSchema(tags=["Classes"])

    query_params = [
        {
            "name": "description",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": "Descrição",
            "schema": {"type": "string"}
        }
    ]
    
    def post(self, request, *args, **kwargs):
        """
           Create Classes receiving a dict, return Classes detail
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_classes = serializer.validated_data
        classes = self.model.objects.create(**new_classes)
        classes.save()
        return JsonResponse({'classes': self.serializer_class(classes, many=False).data}, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """Get Classes details"""
        classess = self.get_query()
        return JsonResponse({'classess': classess})
