"""
This module defines a Api's classes that provides HTTP methods for managing File objects models.
It is extended from an AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
Api's responds with JSON data and uses rest_framework.schemas.openapi.AutoSchema to generate the API documents.
Api's classes use the File model and schema File to work with data.
"""
from django.db import transaction
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser

from file.schemas import FileSchema
from file.models import File, GenericModelPath
from core.abstract.views import AbstractViewApi

from rest_framework import permissions, serializers
from core.permission.views import CheckHasPermission
from file.tasks import SaveFileTask, ProcessExcelTask
from utils import _


class FileApi(AbstractViewApi):
    """Define the FileApi view class for handling HTTP methods related to File.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The FileApi supports HTTP POST and GET methods, and uses the FileSchema
    serializer for input/output validation. The view requires authenticated users with appropriate
    permissions to access the API endpoints, as specified by the IsAuthenticated and CheckHasPermission
    permission classes.

    Attributes:
        http_method_names (list): A list of HTTP methods supported by this view.
        serializer_class (class): The serializer class for input/output validation.
        permission_classes (list): A list of permission classes for user authentication and authorization.
        model (class): The model class associated with this view.

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve file with a matching description:
        ```
        GET /api/v1/file/?file=file_name
        ```
    """
    http_method_names = ['post']
    serializer_class = FileSchema
    parser_classes = (MultiPartParser,)
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = File
    docs = {
        'init': _("""Represents the entire File.
                """),
        'get': _("""This method handles GET requests for the view. It retrieves a specific File object using the given
            calculation_id from the query parameters and serializes the result into JSON format before returning it as
             an HTTP response.

                Returns:
                    JsonResponse: An HTTP response containing the serialized File data retrieved.
                """)
    }

    query_params = [
        {
            "name": "file",
            "field": "file__icontains",
            "in": "query",
            "required": False,
            "description": _("file"),
            "schema": {"type": "string"}
        }
    ]

    @swagger_auto_schema(operation_description='Upload file...', )
    def post(self, request, *args, **kwargs):
        path = kwargs.get('path')
        generic_path = GenericModelPath.objects.filter(path=path).first()
        if not generic_path:
            raise serializers.ValidationError(_('Path not found'))
        serializer = self.get_serializer_class()

        serializer_create = serializer(data=request.data)
        if serializer_create.is_valid(raise_exception=True):
            with transaction.atomic():
                data = serializer_create.validated_data
                file = data["file"]
                object_id = data['object_id']

                model = generic_path.content_object.model_class().objects.filter(id=object_id).first()
                if not model:
                    raise serializers.ValidationError(_('Object not found'))

                file_obj = self.model(file=file, object_id=data['object_id'], generic_path=generic_path,
                                      content_object=model)
                file_obj.save()
                model.parse_file(file_obj)
                # file_read = file_obj.file.read()
                # task = ProcessExcelTask.delay('task-process-excel-to-json', file_read)
                # SaveFileTask.delay(task.id, file_obj.id)

        serializer_data = serializer(file_obj).data
        return JsonResponse(serializer_data)


class FileDetailApi(AbstractViewApi):
    """Define the FileApi view class for handling HTTP methods related to File.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The FileApi supports HTTP POST and GET methods, and uses the FileSchema
    serializer for input/output validation. The view requires authenticated users with appropriate
    permissions to access the API endpoints, as specified by the IsAuthenticated and CheckHasPermission
    permission classes.

    Attributes:
        http_method_names (list): A list of HTTP methods supported by this view.
        serializer_class (class): The serializer class for input/output validation.
        permission_classes (list): A list of permission classes for user authentication and authorization.
        model (class): The model class associated with this view.

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve file with a matching description:
        ```
        GET /api/v1/file/?file=file_name
        ```
    """
    http_method_names = ['get']
    serializer_class = FileSchema
    parser_classes = (MultiPartParser,)
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = File
    docs = {
        'init': _("""Represents the entire File.
                    """),
        'get': _("""This method handles GET requests for the view. It retrieves a specific File object using the given
                calculation_id from the query parameters and serializes the result into JSON format before returning it as
                 an HTTP response.

                    Returns:
                        JsonResponse: An HTTP response containing the serialized File data retrieved.
                    """)
    }
