"""
This module defines a Api's classes that provides HTTP methods for managing DttUser objects models.
It is extended from an AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
Api's responds with JSON data and uses rest_framework.schemas.openapi.AutoSchema to generate the API documents.
Api's classes use the DttUser model and schema DttUser to work with data.
"""
from config.settings import ENABLE_SSO, IS_LOCALHOST, PASSWD_DEV
from core.abstract.views import AbstractViewApi
from core.dttuser.schemas import UserDttSchema, UserAuthorizeDttSchema
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from core.permission.views import CheckHasPermission, CreatePermissions
from utils import get_user_model
from rest_framework import permissions


User = get_user_model()


class AbstractUserDttApi(AbstractViewApi):
    """HTTP methods for interfacing with the User Deloitte modelThis method returns a JSON response that contains the user details given a filtering criteria. 
    The serializer is used to access the model object, and then the data is returned in a JSON format."""
    serializer_class = UserDttSchema

    if IS_LOCALHOST:
        permission_classes = [permissions.AllowAny]
    else:
        permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = User
    queryset = User.objects.all
    schema = AutoSchema(tags=["User"])

    query_params = [
        {
            "name": "nome",
            "field": "first_name__icontains",
            "in": "query",
            "required": False,
            "description": "Nome do usuário",
            "schema": {"type": "string"}
        },
        {
            "name": "username",
            "field": "username__icontains",
            "in": "query",
            "required": False,
            "description": "Username do usuário",
            "schema": {"type": "string"}
        },
        {
            "name": "is_active",
            "field": "is_active__exact",
            "in": "query",
            "required": False,
            "description": "Usuários Autenticados (True/False)",
            "schema": {"type": "string"}
        },
    ]


class UserDttDetailApi(AbstractUserDttApi):
    """This class represents the HTTP methods for User Deloitte. It contains methods such as get, and objects like query_params and schema."""
    http_method_names = ['get']
    query_params = []
    schema = AutoSchema(
        tags=['User'],
        component_name='UserDetail',
        operation_id_base='UserDetail',
    )

    def get(self, request, *args, **kwargs):
        """
        This method returns a JSON response that contains the user details as per authenticated user. 
        The serializer is used to access the model object, and then the data is returned in a JSON format.
        """
        serializer = self.get_serializer_class()
        user = serializer(self.model.objects.filter(
            id=request.user.id).first(), many=False).data
        return JsonResponse({'user': user})

class UserAuthorizeDttApi(AbstractUserDttApi):
    """This class represents the HTTP methods for User Deloitte. It contains methods such as get, and objects like query_params and schema."""
    http_method_names = ['post']
    serializer_class = UserAuthorizeDttSchema
    query_params = []
    schema = AutoSchema(
        tags=['User'],
        component_name='UserAuthorize',
        operation_id_base='UserAuthorize',
    )

    def post(self, request, *args, **kwargs):
        """
        This method returns a JSON response that contains the user details as per authenticated user. 
        The serializer is used to access the model object, and then the data is returned in a JSON format.
        """
        serializer = self.get_serializer_class()
        user = serializer(self.model.objects.filter(
            email=request.user.email).first(), many=False).data
        user.is_active = True
        user.update()
        return JsonResponse({'user': user}, status=status.HTTP_201_CREATED)

class UserDttApi(AbstractUserDttApi):
    """HTTP methods for interacting with Deloitte user data."""
    http_method_names = ['post', 'get']

    def post(self, request, *args, **kwargs):
        """
        Create a new user by recieving data in the form of dictionaries and 
        returning the specific user details.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_user = serializer.validated_data
        groups = new_user.pop('groups', [])  # TODO: adicionar grupo ao projeto
        new_user.pop('password_confirm', None)
        password = new_user.pop('password', None)
        user = self.model.objects.create(**new_user)
        user.set_password(password)
        user.groups.add(groups)
        user.save()

        if IS_LOCALHOST:
            user_authenticated = authenticate(
                username=new_user['username'], password=password)
            if user_authenticated:
                login(self.request, user_authenticated)
        serializer = self.get_serializer_class()
        return JsonResponse({'user': serializer(request.user, many=False).data}, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """Get the details of all existing users."""
        users = self.get_query()
        return JsonResponse({'users': users})


if ENABLE_SSO is False:
    user, created = User.objects.get_or_create(
        username='dev_admin', first_name='admin', last_name='dev', is_staff=True)
    user.set_password(PASSWD_DEV)
    project_manager_list, created, group_manager = CreatePermissions().create_project_manager()
    user.groups.add(group_manager)
    user.save()

    user, created = User.objects.get_or_create(
        username='dev_user', first_name='user', last_name='dev', is_staff=False)
    user.set_password(PASSWD_DEV)
    user.save()
