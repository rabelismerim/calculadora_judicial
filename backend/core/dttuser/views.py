"""
This module defines a Api's classes that provides HTTP methods for managing DttUser objects models.
It is extended from an AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
Api's responds with JSON data and uses rest_framework.schemas.openapi.AutoSchema to generate the API documents.
Api's classes use the DttUser model and schema DttUser to work with data.
"""
from config.settings import ENABLE_SSO, IS_LOCALHOST, PASSWD_DEV
from core.abstract.views import AbstractViewApi
from core.dttuser.schemas import UserDttSchema, UserAuthorizeDttSchema, GroupSchema, SubgroupSchema, UserMailDttSchema
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from core.permission.views import CheckHasPermission, CreatePermissions
from utils import get_user_model
from rest_framework import permissions, serializers
from django.contrib.auth.models import Group
from core.dttuser.models import Subgroup

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
    schema = AutoSchema(tags=["Users"])

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
            "field": "is_active",
            "in": "query",
            "required": False,
            "description": "Usuários Autorizados (True/False)",
            "schema": {"type": "bool"}
        },
    ]


class UserDttDetailApi(AbstractUserDttApi):
    """This class represents the HTTP methods for User Deloitte. It contains methods such as get, and objects like query_params and schema."""
    http_method_names = ['get']
    query_params = []
    schema = AutoSchema(
        tags=['Users'],
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
        tags=['Users'],
        component_name='UserAuthorize',
        operation_id_base='UserAuthorize',
    )

    def post(self, request, *args, **kwargs):
        """
        This method returns a JSON response that contains the user details as per authenticated user. 
        The serializer is used to access the model object, and then the data is returned in a JSON format.
        """

        serializer = self.get_serializer_class()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_filter = serializer.validated_data
        groups = user_filter.pop('groups', [])
        subgroups = user_filter.pop('subgroups', [])

        user_approved = self.model.objects.filter(**user_filter).first()
        if not user_approved:
            raise serializers.ValidationError(['Email não encontrado'])

        user_approved.is_active = user_filter.is_active
        user_approved.groups.add(*groups)
        user_approved.subgroups.add(*subgroups)
        user_approved.save()

        return JsonResponse({'user': user_filter}, status=status.HTTP_201_CREATED)


class UserSendMailDttApi(AbstractUserDttApi):
    """This class represents the HTTP methods for User Deloitte. It contains methods such as get, and objects like query_params and schema."""
    http_method_names = ['post']
    serializer_class = UserMailDttSchema
    query_params = []
    schema = AutoSchema(
        tags=['Users'],
        component_name='UserMail',
    )

    def post(self, request, *args, **kwargs):
        """
        This method returns a JSON response that contains the user details as per authenticated user. 
        The serializer is used to access the model object, and then the data is returned in a JSON format.
        """

        serializer = self.get_serializer_class()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_filter = serializer.validated_data

        user_mail = self.model.objects.filter(**user_filter).first()
        if not user_mail:
            raise serializers.ValidationError(['Email não encontrado'])

        for item in user_mail:
            send_mail('Liberação de Uso - ' + item.email,
                      'Esse email é enviado automaticamente pelo sistema para solicitação de liberação do usuário ' + item.email + ' ao sistema. Para liberar o acesso favor entrar no painel de administração e cadastrar o mesmo ao sistema.',
                      None)

        return JsonResponse({'user': user_filter}, status=status.HTTP_201_CREATED)


class GroupApi(AbstractViewApi):
    """HTTP methods for interfacing with the User Deloitte modelThis method returns a JSON response that contains the user details given a filtering criteria. 
    The serializer is used to access the model object, and then the data is returned in a JSON format."""
    serializer_class = GroupSchema

    if IS_LOCALHOST:
        permission_classes = [permissions.AllowAny]
    else:
        permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Group
    http_method_names = ['get']
    schema = AutoSchema(tags=["Groups"])


class SubgroupApi(AbstractViewApi):
    """HTTP methods for interfacing with the User Deloitte modelThis method returns a JSON response that contains the user details given a filtering criteria. 
    The serializer is used to access the model object, and then the data is returned in a JSON format."""
    serializer_class = SubgroupSchema

    if IS_LOCALHOST:
        permission_classes = [permissions.AllowAny]
    else:
        permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Subgroup
    http_method_names = ['get']
    schema = AutoSchema(tags=["Subgroups"])


class UserDttApi(AbstractUserDttApi):
    """HTTP methods for interacting with Deloitte user data."""
    http_method_names = ['post', 'get']

    def post(self, request, *args, **kwargs):
        """
        Create a new user by receiving data in the form of dictionaries and 
        returning the specific user details.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_user = serializer.validated_data
        groups = new_user.pop('groups', [])
        subgroups = new_user.pop('subgroups', [])
        new_user.pop('password_confirm', None)
        password = new_user.pop('password', None)
        user = self.model.objects.create(**new_user)
        user.set_password(password)
        user.groups.add(*groups)
        user.groups.add(*subgroups)
        user.save()

        if IS_LOCALHOST:
            user_authenticated = authenticate(
                username=new_user['username'], password=password)
            if user_authenticated:
                login(self.request, user_authenticated)
        serializer = self.get_serializer_class()
        return JsonResponse({'user': serializer(request.user, many=False).data}, status=status.HTTP_201_CREATED)


if ENABLE_SSO is False:
    try:
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
    except Exception as e:
        print(e, 'err create user\n\n')
