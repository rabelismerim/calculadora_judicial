import datetime
from abc import ABC

import uritemplate
from django.http import JsonResponse
from django.utils.encoding import smart_str, force_str
from rest_framework import generics, serializers, status
from rest_framework.filters import BaseFilterBackend
from rest_framework.generics import get_object_or_404
from rest_framework.schemas.utils import get_pk_description
from rest_framework.utils import formatting
from rest_framework.schemas.openapi import AutoSchema

from core.drfmsal.schemas import CustomDictField
from utils import _


class CustomSchema(AutoSchema):

    def get_operation_id_base(self, path, method, action):
        view = self.view
        if hasattr(view, 'operation_id_base') and isinstance(view.operation_id_base, str):
            return view.operation_id_base
        return super(CustomSchema, self).get_operation_id_base(path, method, action)

    def get_operation(self, path, method):
        op = super(CustomSchema, self).get_operation(path, method)
        op['parameters'] = list(map(lambda x: {**x, 'description': str(x['description'])}, op['parameters']))
        return op

    def get_tags(self, path, method):
        view = self.view
        if hasattr(view, 'tags') and isinstance(view.tags, list):
            return list(map(str, view.tags))
        if view.model:
            app = view.model._meta.app_config.name.split('.')[0].capitalize()
            app_label = view.model._meta.app_label.capitalize()
            if app == app_label:
                return ['{}'.format(app)]
            return ['{} - {}'.format(app, app_label)]
        return super(CustomSchema, self).get_tags(path, method)

    def map_field(self, field):
        if isinstance(field, CustomDictField):
            return {
                'type': 'any',
            }
        return super(CustomSchema, self).map_field(field)

    def get_description(self, path, method):
        view = self.view
        init = self._get_init_description()
        method_name = getattr(view, 'action', method.lower())
        method_docstring = getattr(view, method_name, None).__doc__
        if hasattr(view, 'docs') and isinstance(view.docs, dict) and view.docs.get(method.lower()):
            method_docstring = view.docs.get(method.lower())
            docstring = self._get_description_section(view, method.lower(),
                                                      formatting.dedent(smart_str(method_docstring)))

        elif method_docstring:
            docstring = self._get_description_section(view, method.lower(),
                                                      formatting.dedent(smart_str(method_docstring)))
        else:
            docstring = self._get_description_section(view, getattr(view, 'action', method.lower()),
                                                      view.get_view_description())

        return formatting.dedent(smart_str(init + '\r\n' + str(docstring)))

    def _get_init_description(self) -> str:
        view = self.view
        if hasattr(view, 'docs') and isinstance(view.docs, dict) and view.docs.get('init'):
            return view.docs.get('init')
        return ''


class SimpleFilterBackend(BaseFilterBackend, ABC):
    def get_schema_operation_parameters(self, view):
        return view.query_params


class AbstractViewApi(generics.GenericAPIView):
    """HTTP methods for Api VIew"""
    filter_backends = (SimpleFilterBackend,)
    query_params = []
    model = None
    schema = CustomSchema()

    def get_serializer_class(self):
        if hasattr(self, 'layout_serializers'):
            return self.layout_serializers.get(self.request.method.lower(), self.layout_serializers['default'])
        return super(AbstractViewApi, self).get_serializer_class()

    @staticmethod
    def get_schema_operation_parameters(view):
        return view.query_params

    @staticmethod
    def __parse_date(date_string):
        """Parse string to date"""
        return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()

    @staticmethod
    def __parse_datetime(date_string):
        """Parse string to datetime"""
        return datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M')

    @staticmethod
    def __parse_bool(text):
        """Parse string to bool"""
        return str(text).lower() in 'true'

    def __get_type_by_instance(self, instance):
        """Get instance, type, parser and legend by field schema type"""
        types = {
            'string': {'type': str, 'parser': str, 'legend': 'string'},
            'date': {'type': datetime.date, 'parser': self.__parse_date, 'legend': '2001-12-30'},
            'datetime': {'type': datetime.date, 'parser': self.__parse_datetime, 'legend': '2001-12-30 23:01'},
            'float': {'type': float, 'parser': float, 'legend': '01.00'},
            'int': {'type': int, 'parser': int, 'legend': '1'},
            'bool': {'type': bool, 'parser': self.__parse_bool, 'legend': 'True/False'},
        }

        return types.get(instance, str)

    def get_query(self, id_=None, **kwargs):
        """Validate parameters received in query params, returning query values"""
        query = self.get_queryset()
        exclude = self.__get_exclude_values()

        for valid_params in self.query_params:
            type_instance = valid_params['schema']['type']
            field = valid_params['field']
            name = valid_params['name']
            value = self.request.query_params.get(name)
            if value:
                instance = self.__get_type_by_instance(type_instance)
                try:
                    value = instance['parser'](value)
                except:
                    pass
                if isinstance(value, instance['type']):
                    query[field] = value
                else:
                    raise serializers.ValidationError(
                        {name: _('Field in invalid format. It must be in the format{}').format(instance["legend"])})
        serializer = self.get_serializer_class()
        if id_:
            return serializer(self.model.objects.filter(id=id_, **query, **kwargs).first(), many=False,
                              exclude=exclude).data
        return serializer(self.model.objects.filter(**query, **kwargs).distinct(), many=True, exclude=exclude).data

    def get(self, request, *args, **kwargs):
        """Abstract method for default get model. Overide method in class for custom operation"""
        id_ = kwargs.get('id')
        query = self.get_query(id_=id_)
        model_name = self.model._meta.verbose_name_plural.lower(
        ) if not id_ else self.model._meta.verbose_name.lower()
        return JsonResponse({model_name.replace(' ', '_'): query})

    def post(self, request, *args, **kwargs):
        """Abstract method for default post model. Overide method in class for custom operation"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_obj = serializer.validated_data
        obj = self.model.objects.create(**new_obj)
        obj_name = self.model._meta.verbose_name_plural.lower().replace(' ', '_')
        return JsonResponse({obj_name: self.serializer_class(obj, many=False).data}, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        """
        This method handles PUT requests for the view. It expects input data that conform to the serializer used by
        the view class. It updates the approved_calculation or date object of a specific comparative object using the
        given calculation_id from the query parameters and serializes the updated object in JSON format before
        returning it as an HTTP response.

        Parameters: request: The HTTP request object. args: Any additional positional arguments passed to the method.
        kwargs: Any additional keyword arguments passed to the method, with calculation_id identifying the
        comparative object to update. Returns: JsonResponse: An HTTP response containing the updated and serialized
        comparative object data.
        """
        id_ = kwargs.get('id')
        exclude = self.__get_exclude_values()
        try:
            serializer = self.serializer_class(
                data=request.data, exclude=exclude)
        except ValueError:
            serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data_obj = dict(serializer.validated_data)
        obj = get_object_or_404(self.model, id=id_)
        obj.dict_update(**data_obj)
        model_name = self.model._meta.verbose_name.lower().replace(' ', '_')
        return JsonResponse({model_name: self.serializer_class(obj, many=False).data})

    def __get_exclude_values(self) -> list or tuple:
        if hasattr(self, 'exclude') and (isinstance(self.exclude, list) or isinstance(self.exclude, tuple)):
            return self.exclude
        return []

    def get_queryset(self):
        return {}
