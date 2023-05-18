from rest_framework import permissions

from utils import _, get_user_model
from .serializers import UserSerializer
from ...abstract.views import AbstractViewApi
from ...permission.views import CheckHasPermission

User = get_user_model()


class UserListView(AbstractViewApi):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = User
    docs = {
        'init': _("""The `User` class represents a user on the system, has common properties such as `username` 
            `email`, `full_name`.
            """),
        'get': _("""Get the list of all users active. Can filter a user by `username`, `email`, `first_name` or 
        `last_name`.
        """)
    }
    http_method_names = ['get']
    query_params = [
        {
            "name": "username",
            "field": "username__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Username")),
            "schema": {"type": "string"}
        },
        {
            "name": "email",
            "field": "email__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Email")),
            "schema": {"type": "string"}
        },
        {
            "name": "first_name",
            "field": "first_name__icontains",
            "in": "query",
            "required": False,
            "description": str(_("First Name")),
            "schema": {"type": "string"}
        },
        {
            "name": "last_name",
            "field": "last_name__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Lastname")),
            "schema": {"type": "string"}
        },
        {
            "name": "is_active",
            "field": "is_active",
            "in": "query",
            "required": False,
            "description": str(_("Authorized Users (True/False)")),
            "schema": {"type": "bool"}
        },
    ]

    def get_queryset(self):
        return {'is_active': True}
