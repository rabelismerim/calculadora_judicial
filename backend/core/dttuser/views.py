from http.client import IM_USED
from re import I
from core.abstract.views import AbstractViewApi
from core.dttuser.schemas import UserDttSchema
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from utils import get_user_model
from rest_framework import permissions 

User = get_user_model()


class UserDttApi(AbstractViewApi):
    """HTTP methods for User Deloitte"""
    # permission_classes = (IsAuthenticatedOrWriteOnly,)
    http_method_names = ['post', 'get']
    serializer_class = UserDttSchema
    permission_classes = [permissions.IsAdminUser]
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
        new_user.pop('password_confirm', None)
        password = new_user.pop('password', None)
        user = User.objects.create(**new_user)
        user.set_password(password)
        user.save()
        return JsonResponse({'user': UserDttSchema(user, many=False).data}, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """Get Users details"""
        params = self.get_query_params()
        users = self.queryset().filter(**params)
        users = self.serializer_class(users, many=True).data
        return JsonResponse({'users': users})