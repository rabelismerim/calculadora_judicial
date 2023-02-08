from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission
from projects.judge.models import Judge
from projects.judge.schemas import JudgeSchema


class JudgeApi(AbstractViewApi):
    """HTTP methods for judge"""
    http_method_names = ['post', 'get']
    serializer_class = JudgeSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Judge
    schema = AutoSchema(tags=["Project - Judge"])

    query_params = [
        {
            "name": "nome",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": "Nome do Juiz",
            "schema": {"type": "string"}
        }
    ]

    def post(self, request, *args, **kwargs):
        """
           Create judge receiving a dict, return judge detail
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_judge = serializer.validated_data
        judge = self.model.objects.create(**new_judge)
        judge.save()
        return JsonResponse({'judge': self.serializer_class(judge, many=False).data}, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """Get judges details"""
        judges = self.get_query()
        return JsonResponse({'judges': judges})
