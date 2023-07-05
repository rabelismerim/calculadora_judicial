from django.http import JsonResponse
from django_celery_results.models import TaskResult
from rest_framework import permissions, status

from base.schemas import TaskResultSerializer
from core.abstract.models import UpdateUser
from core.abstract.schemas import UpdateModelSchema
from core.abstract.views import AbstractViewApi
from core.permission.views import CheckHasPermission
from utils import doc, _


class UpdateUserApi(AbstractViewApi):
    """This class provides basic HTTP methods for managing Calculation Objects.
    It includes a serializer_class and required permission_classes to authenticate the users,
    a model instance with a corresponding schema as well as custom query parameters to retrieve data.
    """
    serializer_class = UpdateModelSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = UpdateUser

    http_method_names = ['get']
    tags = [_('Base - Historic')]

    @doc(_("""Method to obtain the entire history of changes for a given object, filtering the changes by the ID 
    received

    Returns a JSON Response with the list of changes"""))
    def get(self, request, *args, **kwargs):
        updates = self.model.objects.filter(object_id=kwargs.get('id'))
        serializer = self.serializer_class(updates, many=True)
        return JsonResponse({'historic': serializer.data}, status=status.HTTP_201_CREATED)


class TaskStatusApi(AbstractViewApi):
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
    serializer_class = TaskResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    model = TaskResult
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

    @doc(_("""Method to obtain the entire history of changes for a given object, filtering the changes by the ID 
       received

       Returns a JSON Response with the list of changes"""))
    def get(self, request, *args, **kwargs):
        updates = self.model.objects.filter(task_id=kwargs.get('id')).first()
        serializer = self.serializer_class(updates, many=False)
        return JsonResponse({'task': serializer.data}, status=status.HTTP_200_OK)
