from core.abstract.views import AbstractViewApi
from django.http import JsonResponse

from rest_framework import permissions, serializers, status
from core.permission.views import CheckHasPermission
from rates.models import Rate, RateFile, Template
from rates.schemas import RateFileSchema, RateSchema, TemplateSchema, TemplateListSchema
from utils import _, doc


class RateApi(AbstractViewApi):
    """HTTP methods for Rate"""
    http_method_names = ['post', 'get']
    serializer_class = RateSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Rate

    docs = {
        'init': _("""Represents the indices that can be applied to rates to calculate debt updates.
        """),
        'get': _("""Returns the rate and its accumulated values, period and date""")
    }

    query_params = [
        {
            "name": "rate",
            "field": "index__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Rate")),
            "schema": {"type": "string"}
        }
    ]

    @doc(_("""Saves an index according to its name and values"""))
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_rate = serializer.validated_data
        return JsonResponse({'rate': self.serializer_class(new_rate, many=False).data}, status=status.HTTP_201_CREATED)


class RateFileApi(AbstractViewApi):
    """HTTP methods for rate_file"""
    http_method_names = ['post']
    serializer_class = RateFileSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Rate

    query_params = [
        {
            "name": "rate",
            "field": "index__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Rate")),
            "schema": {"type": "string"}
        }
    ]

    @doc(_("""Updating or creating rates through an excel file. Saves an rate using an excel file. This file must contain 
        the columns mes and indice. Optionally according to the rate have the fields acumulado and periodo"""))
    def post(self, request, *args, **kwargs):
        data = request.data
        file = request.FILES.get('file')
        index_name = data.get('index')

        if not index_name:
            raise serializers.ValidationError([_('Required field index')])

        if not file:
            raise serializers.ValidationError([_('Required field file')])

        new_index, created = Rate.objects.get_or_create(index=index_name)
        filename = file.name

        old_file = new_index.get_ratefile()
        if old_file:
            new_file = old_file
        else:
            new_file = RateFile()
            new_file.rate = new_index

        new_file.file.save(file.name, file)
        new_file.save()
        rows = new_file.get_excel_to_dict()

        if rows is False:
            raise serializers.ValidationError(
                [_('The file {} does not contain the correct fields. Required at least the column mes and indice, '
                   f'acumulado and periodo are optional').format(filename)])

        if len(rows) == 0:
            raise serializers.ValidationError(
                [_('The file {} is empty').format(filename)])

        for new_rate in rows:
            serializer = RateSchema(data=new_rate)
            serializer.is_valid(raise_exception=False)

        return JsonResponse({'rate': RateSchema(new_index, many=False).data}, status=status.HTTP_201_CREATED)


class TemplateApi(AbstractViewApi):
    """HTTP methods for Template"""
    http_method_names = ['get']
    serializer_class = TemplateListSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Template

    query_params = [
        {
            "name": "name",
            "field": "name__icontains",
            "in": "query",
            "required": False,
            "description": _("Name"),
            "schema": {"type": "string"}
        }
    ]

    docs = {
        'get': _("""Example of how templates should look for each selected rate type
            Returns a list of templates with their id and name""")
    }


class TemplateDetailApi(AbstractViewApi):
    """HTTP methods for Template"""
    http_method_names = ['get']
    serializer_class = TemplateSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Template

    query_params = []

    docs = {
        'get': _("""Example of how templates should look for each selected rate type
        Returns a detail of template with their id, name, tables and fields in tables""")
    }
