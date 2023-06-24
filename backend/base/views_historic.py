from django.http import JsonResponse
from rest_framework import permissions, status

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
