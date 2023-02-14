from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.entity.models import Entity
from recovering.archive.models import Archive
from recovering.archive_recovering.models import ArchiveRecovering
from recovering.models import Recovering
from recovering.schemas import RecoveringSchema


class AbstractRecoveringApi(AbstractViewApi):
    """HTTP methods for Recovering"""
    http_method_names = ['post', 'get']
    serializer_class = RecoveringSchema
    permission_classes = [permissions.IsAdminUser]
    model = Recovering
    schema = AutoSchema(tags=["Recovering"])

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


class RecoveringApi(AbstractRecoveringApi):
    """HTTP methods for recovering"""
    http_method_names = ['get', 'post']

    def post(self, request, *args, **kwargs):
        """
           Create recovering receiving a dict, return recovering detail
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        recovering = serializer.validated_data
        entity = recovering.pop('entity')
        new_archive_recovering = recovering.pop('archives', None)
        recovering['entity'] = Entity.objects.create(**entity)
        new_recovering = self.model.objects.create(**recovering)
        if new_archive_recovering:
            for new_ in new_archive_recovering:
                archive = new_.pop('archive')
                new_archive = Archive.objects.create(**archive)
                ArchiveRecovering.objects.create(
                    recovering=new_recovering, archive=new_archive)
        return JsonResponse({'recovering': self.serializer_class(new_recovering, many=False).data}, status=status.HTTP_201_CREATED)
