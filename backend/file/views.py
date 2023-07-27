"""
This module defines a Api's classes that provides HTTP methods for managing File objects models.
It is extended from an AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
Api's responds with JSON data and uses rest_framework.schemas.openapi.AutoSchema to generate the API documents.
Api's classes use the File model and schema File to work with data.
"""
from django.apps import apps
from django.db import transaction
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser

from file.schemas import FileSchema, GenericModelPathSchema, FileExamplesSchema, FileBlobExamplesSchema, \
    ErrorFileUpdateSchema, FileListSchema
from file.models import File, GenericModelPath, ErrorFile
from core.abstract.views import AbstractViewApi

from rest_framework import permissions, serializers
from core.permission.views import CheckHasPermission
from utils import _, doc

init = _("""The `File` represents options to attach files to certain objects.""")


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
        'init': init,
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
    @doc(_("""This method handles POST requests to save files according to the specified path. The path is the 
        representation of a model, such as: `dashboard`, `project` and `creditor`. The `object_id` refers to 
        which object will be related to the file.
        
        Returns:
            JsonResponse: A response containing the `file url` information and `task` to track data 
            processing (if any)"""))
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

        serializer_data = serializer(file_obj).data
        return JsonResponse(serializer_data)


class FilePathsApi(AbstractViewApi):
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
    serializer_class = GenericModelPathSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = GenericModelPath
    operation_id_base = 'FilePathListSchema'
    docs = {
        'init': init,
        'get': _("""This method handles GET requests for the view. It retrieves the list of available `paths` to get
         `excel names`.

        Returns:
        JsonResponse: An response containing the serialized File data retrieved.""")
    }


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
    operation_id_base = 'FileSchema'
    model = File
    docs = {
        'init': init,
        'get': _("""This method handles GET requests for the view. It retrieves a specific `file object` using the given 
        file `id`.

        Returns:
            JsonResponse: An response containing the serialized File data retrieved.""")
    }


class FileErrorDetailApi(AbstractViewApi):
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
    http_method_names = ['put', 'delete']
    serializer_class = ErrorFileUpdateSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = ErrorFile
    docs = {
        'init': init,
        'get': _("""This method handles GET requests for the view. It retrieves a specific `file object` using the given 
        file `id`.

        Returns:
            JsonResponse: An response containing the serialized File data retrieved.""")
    }


class FileExamplesApi(AbstractViewApi):
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

    serializer_class = FileExamplesSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = File
    docs = {
        'init': init,
    }

    @doc(_("""This method handles the GET for the view. It retrieves a list of `excel file names` available for
         download, with the given `path`.

        Returns:
            JsonResponse: An response containing the serialized File data retrieved."""))
    def get(self, request, *args, **kwargs):
        path = kwargs.get('path')
        generic_path = GenericModelPath.objects.filter(path=path).first()
        if not generic_path:
            raise serializers.ValidationError(_('Path not found'))
        content_object = generic_path.content_object
        related_model = apps.get_model(content_object.app_label, content_object.model)
        return JsonResponse({'excel_names': related_model().get_list_excels_name()})


class FileExampleDetailApi(AbstractViewApi):
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
    serializer_class = FileBlobExamplesSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = File
    operation_id_base = 'FileSchemaDetail'
    docs = {
        'init': init,
    }

    @doc(_("""This method handles the GET for the view. It generates a downloadable excel file according to the
         provided file `path` and `name`.

        Returns:
            JsonResponse: An response containing the serialized File blob retrieved."""))
    def get(self, request, *args, **kwargs):
        path = kwargs.get('path')
        excel_name = kwargs.get('name')
        generic_path = GenericModelPath.objects.filter(path=path).first()
        if not generic_path:
            raise serializers.ValidationError(_('Path not found'))
        content_object = generic_path.content_object
        related_model = apps.get_model(content_object.app_label, content_object.model)
        excel = related_model().get_excel_by_name(name=excel_name)
        if not excel:
            raise serializers.ValidationError(_('Name not found'))
        return excel.generate_excel_example()


class PathFileListApi(AbstractViewApi):
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
    serializer_class = FileListSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = File
    docs = {
        'init': init,
    }

    @doc(_("""This method handles the GET for the view. It takes the `path` and `object_id` and generates a 
        list of objects with related `file` and `id`

        Returns:
            JsonResponse: An response containing the serialized Files retrieved."""))
    def get(self, request, *args, **kwargs):
        path = kwargs.get('path')
        object_id = kwargs.get('object_id')
        generic_path = GenericModelPath.objects.filter(path=path).first()
        if not generic_path:
            raise serializers.ValidationError(_('Path not found'))
        serializer = self.get_serializer_class()
        files = serializer(self.model.objects.filter(object_id=object_id), many=True).data
        return JsonResponse({'files': files})
