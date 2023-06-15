"""
This module defines a Api's classes that provides HTTP methods for managing DttUser objects models.
It is extended from an AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
Api's responds with JSON data and uses rest_framework.schemas.openapi.AutoSchema to generate the API documents.
Api's classes use the DttUser model and schema DttUser to work with data.
"""
import base64
import hashlib
import uuid

from django.core.files.base import ContentFile
from rest_framework.exceptions import PermissionDenied

from config.settings import IS_LOCALHOST, DTT_EMAIL, ROLES
from core.abstract.views import AbstractViewApi
from core.dttuser.schemas import UserDttSchema, UserAuthorizeDttSchema, GroupSchema, SubgroupSchema, UserMailDttSchema
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.core.mail import send_mail
from rest_framework import status

from core.permission.views import CheckHasPermission, CheckPermissions
from utils import get_user_model, _, doc
from rest_framework import permissions, serializers
from django.contrib.auth.models import Group
from core.dttuser.models import Subgroup

User = get_user_model()

docs = {
    'init': _("""The `User` class represents a user on the system, has common properties such as `username` 
        `email` as well as additional information such as `role`, `status`, `first_name`, `last_name` 
        `userpicture` and `is_active` (if the user is active) He can also be a staff member and have access to the 
        admin site, as controlled by the `is_staff` field, some permission fields that can be used to control access 
        to resources in the system.
        The status(`Active`, `Inactive`, `Pending`, `Rejected`, `Vacation`) controls whether the user is active or 
        inactive.
        """),
}


class AbstractUserDttApi(AbstractViewApi):
    """HTTP methods for interfacing with the User Deloitte modelThis method returns a JSON response that contains the
    user details given a filtering criteria. The serializer is used to access the model object, and then the data is
    returned in a JSON format. """
    serializer_class = UserDttSchema
    docs = docs.copy()
    if IS_LOCALHOST:
        permission_classes = [permissions.AllowAny]
    else:
        permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = User
    allow_cache = False
    query_params = [
        {
            "name": "name",
            "field": "first_name__icontains",
            "in": "query",
            "required": False,
            "description": _("Name"),
            "schema": {"type": "string"}
        },
        {
            "name": "username",
            "field": "username__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Username")),
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


class UserDttDetailApi(AbstractUserDttApi):
    """This class represents the HTTP methods for User Deloitte. It contains methods such as get, and objects like
    query_params and schema. """
    http_method_names = ['get']
    query_params = []
    docs = docs.copy()
    allow_cache = False

    @doc(_("""This method returns a JSON response that contains the user details as per authenticated user. 
        The serializer is used to access the model object, and then the data is returned in a JSON format.
        """))
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()
        user = serializer(self.model.objects.filter(
            id=request.user.id).first(), many=False).data
        return JsonResponse({'user': user})


class UserAuthorizeDttApi(AbstractUserDttApi):
    """This class represents the HTTP methods for User Deloitte. It contains methods such as get, and objects like
    query_params and schema. """
    http_method_names = ['post']
    serializer_class = UserAuthorizeDttSchema
    permission_classes = [permissions.IsAuthenticated, CheckPermissions]
    query_params = []
    perms = ['can_authorize_users']
    docs = docs.copy()
    allow_cache = False

    @doc(_("""Handles HTTP POST request to authorize or unauthorize user access.

        - Validates request data.
        - Alter status by choice.
        - Filters user by email and validates if it exists.
        - Adds specified permission groups and subgroups to the user.
        """))
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_filter = serializer.validated_data
        groups = user_filter.pop('groups', [])
        subgroups = user_filter.pop('subgroups', [])
        role = user_filter.pop('role', None)

        user_approved = self.model.objects.filter(email=user_filter['email']).first()
        if not user_approved:
            raise serializers.ValidationError(
                [_('Email {}, not found').format(user_filter["email"])])
        user_approved.groups.clear()
        user_approved.status = user_filter['status']
        user_approved.groups.add(*groups)
        user_approved.subgroups.add(*subgroups)
        if role:
            user_approved.role = role
        user_approved.save()

        return JsonResponse({'user': UserDttSchema(user_approved).data}, status=status.HTTP_201_CREATED)


class UserSendMailDttApi(AbstractUserDttApi):
    """This class represents the HTTP methods for User Deloitte. It contains methods such as get, and objects like
    query_params and schema. Used to validate and send email when asked to create a new user.
    """
    http_method_names = ['post']
    serializer_class = UserMailDttSchema
    query_params = []
    docs = docs.copy()
    allow_cache = False

    @doc(_("""Used to validate and send email when asked to create a new user.
        The serializer is used to access the model object, and then the data is returned in a JSON format.
        """))
    def post(self, request, *args, **kwargs):
        if not DTT_EMAIL:
            raise serializers.ValidationError(
                [_('DTT sending email not configured')])

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_filter = serializer.validated_data

        user_mail = self.model.objects.filter(**user_filter).first()
        if not user_mail:
            raise serializers.ValidationError(
                [_('Email {}, not found').format(user_filter["email"])])

        send_mail(_('Release of Use - {}').format(user_mail.email),
                  _('This email is automatically sent by the system to request the release of user {} to system. To '
                    'release access, please enter the administration panel and register it at system.').format(
                      user_mail.email), DTT_EMAIL, user_mail)

        return JsonResponse({'user': UserDttSchema(user_mail).data}, status=status.HTTP_201_CREATED)


class GroupApi(AbstractViewApi):
    """
    View API for Groups that contains a name and a list of permissions
    and defines what permissions the user has and what he can do within the system.

    Methods:
    - get: Returns a list of groups with their names and permissions.
    """
    allow_cache = False
    serializer_class = GroupSchema
    docs = {
        'init': _("""The `Group` class represents a group of users on the system. Contains common properties for 
        managing user permissions and relationships with the group. It contains a `name` property to identify the group 
        and also a  `permissions` field to define the permissions assigned to the group. Users can be added to a group,
             which allows access to users belonging to a specific group. The available groups are: `Financial Manager`,
              `Calculation Manager`, `Legal Manager`, `Financial Consultant`, `Calculation Consultant` and 
              `Legal Consultant`.
            """),
        'get': _("""The Group contains a name and a list of permissions. Groups define what 
        permissions the user has and what he can do within the system.
        Returns a list of groups.
        """)
    }

    if IS_LOCALHOST:
        permission_classes = [permissions.AllowAny]
    else:
        permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Group
    http_method_names = ['get']

    def get_exclude_queryset(self):
        return {'name__in': ROLES}


class SubgroupApi(AbstractViewApi):
    """
    View API for Subgroups that contains a name and a list of permissions
    and defines what permissions the user has and what he can do within the system.

    Methods:
    - get: Returns a list of groups with their names and permissions.
    """
    serializer_class = SubgroupSchema
    docs = {
        'init': _("""The `Subgroup` class represents a group of users on the system. Contains common properties for 
        managing user permissions and relationships with the group. It contains a `name` property to identify the group 
        and also a  `permissions` field to define the permissions assigned to the group. Users can be added to a group,
             which allows access to users belonging to a specific group. The available groups are: `Financial Manager`,
              `Calculation Manager`, `Legal Manager`, `Financial Consultant`, `Calculation Consultant` and 
              `Legal Consultant`.
            """),
        'get': _("""The Subgroup contains a name and a list of permissions. Groups define what 
            permissions the user has and what he can do within the system.Returns a list of groups.
            """)
    }
    if IS_LOCALHOST:
        permission_classes = [permissions.AllowAny]
    else:
        permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Subgroup
    http_method_names = ['get']
    allow_cache = False

    def get_exclude_queryset(self):
        return {'name__in': ROLES}


class UserDttApi(AbstractUserDttApi):
    """HTTP methods for interacting with Deloitte user data."""
    http_method_names = ['post', 'get']
    docs = {
        'init': _("""The `User` class represents a user on the system, has common properties such as `username` 
        `email`, `password`, as well as additional information such as `role` , `status` , `first_name`, `last_name` 
        `userpicture ` and `is_active` (if the user is active) He can also be a staff member and have access to the 
        admin site, as controlled by the `is_staff` field, some permission fields that can be used to control access 
        to resources in the system.
        The status(`Active`, `Inactive`, `Pending`, `Rejected`, `Vacation`) controls whether the user is active or 
        inactive.
        """),
        'get': _("""Get the list of all users. Include user fields like  `name`, `userpicture`, `permissions list`, etc.
        Can filter a user by `username`, `email`, `first_name`, `last_name` or `is_active`.
        """)
    }
    operation_id_base = 'UserDetail'
    allow_cache = False

    @doc(_("""Only LocalHost. Create a new user by receiving data in the form of dictionaries and 
        returning the specific user details.
        """))
    def post(self, request, *args, **kwargs):
        if IS_LOCALHOST is False:
            raise PermissionDenied()
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

        user_authenticated = authenticate(
            username=new_user['username'], password=password)
        if user_authenticated:
            login(self.request, user_authenticated)
        serializer = self.get_serializer_class()
        return JsonResponse({'user': serializer(request.user, many=False).data}, status=status.HTTP_201_CREATED)
#
users = User.objects.all()
for x in users:
    if x.userpicture:
        data = ContentFile(base64.b64decode(x.userpicture))
        image_data = base64.b64decode(x.userpicture)
        file_hash = hashlib.md5(image_data).hexdigest()
        file_name = f"{file_hash}.jpeg"
        if x.user_img and str(x.user_img.name) in file_name is False:
            x.user_img.save(file_name, data, save=True)  # image is User's model field
            x.save()
