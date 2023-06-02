"""
This module defines a Api's classes that provides HTTP methods for managing BigNumber objects models.
It is extended from an AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
Api's responds with JSON data and uses rest_framework.schemas.openapi.AutoSchema to generate the API documents.
Api's classes use the BigNumber model and schema BigNumber to work with data.
"""
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import JsonResponse
from big_number.schemas import BigNumberSchema
from big_number.models import BigNumber, BigNumberMethod
from core.abstract.views import AbstractViewApi

from rest_framework import permissions, serializers
from core.permission.views import CheckHasPermission
from dashboard.models import QUERY_DASHBOARD
from projects.models import Project
from utils import _, doc


class BigNumberApi(AbstractViewApi):
    """
    API to retrieve data related to big numbers.

    Attributes:
    - model (django.db.models.Model): Model instance representing a big number.

    Methods:
    - get(request, *args, **kwargs):
        Retrieves a specific big number object by its ID and a path.
        Returns the serialized data in JSON format.
        Raises a ValidationError if path is not found or ID is not found.

    - get_dynamic_methods():
        Gets a list of all available dynamic methods.
        Returns a QuerySet of all big number objects.
    """
    http_method_names = ['get']
    serializer_class = BigNumberSchema
    permission_classes = [permissions.IsAuthenticated]
    model = Project  # TODO define permissions
    query_params = QUERY_DASHBOARD
    """O BigNumber representa os valores de kpis, métricas ou gráficos para mensurar a utilização, quantidade ou soma de 
    determinados objetos, como a quantidade de acesso ao longo do mês, o total de credores em determinados projetos, ou
    a quantidade de cálculos para determinado credor"""
    docs = {
        'init': _("""The BigNumber represents the values of kpis, metrics or graphs to measure the use, quantity or 
        sum of certain objects, such as the number of accesses throughout the month, the total number of creditors in 
        certain projects, or the number of calculations for a certain creditor"""),
    }

    @doc(_("""Retrieves the BigNumbers of an object filtered by its `path` and `ID`.
        Returns serialized data in JSON format.
        Throws a ValidationError if the `path` is not found or the `ID` is not found.
        """))
    def get(self, request, *args, **kwargs):
        id_ = kwargs.get('id')
        path = kwargs.get('path')
        filters = {}
        if id_:
            filters['id'] = id_
        serializer = self.get_serializer_class()
        big_number = BigNumber.objects.filter(path=path).first()

        if not big_number:
            raise serializers.ValidationError(_('Path not found'))

        methods_list = big_number.bignumbermethod_set.all()
        self.model = big_number.content_object.model_class().objects.filter(**filters).first()
        if not self.model:
            raise serializers.ValidationError(_('ID not found'))

        option = {
            'GET': 'view',
            'PUT': 'change',
            'POST': 'add',
            'DELETE': 'delete',
        }
        has_perm = request.user.has_permission(f'{option.get(request.method)}_{self.model._meta.verbose_name.lower()}')
        if not has_perm:
            raise PermissionDenied()
        serializer = serializer(self.model, methods_list=methods_list, context={'request': self.request})
        serialized_data = serializer.data
        return JsonResponse(serialized_data, safe=False)

    def get_dynamic_methods(self):
        """
        Gets a list of all available dynamic methods.
        Returns a QuerySet of all big number objects.
        """
        return BigNumber.objects.all()

    def get_dynamic_methods_by_path(self):
        """
        Gets a list of all available dynamic methods.
        Returns a QuerySet of all big number objects.
        """
        return BigNumberMethod.objects.filter(Q(big_number__content_object__model=self.model._meta.verbose_name) | Q(
            big_number__content_object__model=self.model))
