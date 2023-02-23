from http.client import IM_USED
from re import I
from config.settings import ENABLE_SSO, IS_LOCALHOST, PASSWD_DEV
from core.abstract.views import AbstractViewApi
from core.dttuser.schemas import UserDttSchema
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from core.permission.views import CheckHasPermission, CreatePermissions
from utils import get_user_model
from rest_framework import permissions


User = get_user_model()


class UserDttApi(AbstractViewApi):
    """HTTP methods for User Deloitte"""
    http_method_names = ['post', 'get']
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
    ]

    def post(self, request, *args, **kwargs):
        """
           Create User receiving a dict, return user detail
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_user = serializer.validated_data
        groups = new_user.pop('groups', [])  # TODO: adicionar grupo ao projeto
        new_user.pop('password_confirm', None)
        password = new_user.pop('password', None)
        user = self.model.objects.create(**new_user)
        user.set_password(password)
        user.save()

        if IS_LOCALHOST:
            user_authenticated = authenticate(
                username=new_user['username'], password=password)
            if user_authenticated:
                login(self.request, user_authenticated)
        return JsonResponse({'user': UserDttSchema(user, many=False).data}, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """Get Users details"""
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
