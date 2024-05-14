import datetime
import inspect
import json
import os
from abc import ABC
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

from django.apps import apps
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db import transaction, models
from django.http import JsonResponse, Http404
from django.template.response import ContentNotRenderedError
from django.urls import resolve
from django.utils.encoding import smart_str
from drf_yasg import openapi
from rest_framework import generics, serializers, status
from rest_framework.filters import BaseFilterBackend, OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.relations import ManyRelatedField
from rest_framework.schemas.utils import is_list_view
from rest_framework.utils import formatting
from rest_framework.schemas.openapi import AutoSchema

from base.schemas import AbstractDescriptionSchema
from config.settings import ENABLE_CACHE
from core.drfmsal.schemas import CustomDictField
from core.permission.views import CheckAPIVersion
from security.views import Security
from utils import _

cache.clear()


def get_app_label_from_model(model) -> str:
    """Extracts app label from a Django model and returns it."""
    app = model._meta.app_config.name.split('.')[0]
    try:
        return str(apps.get_app_config(app).verbose_name)
    except LookupError:
        pass
    return app


class CustomSchema(AutoSchema):
    """
    A custom schema for generating OpenAPI 3.0.0 spec for DRF views.

    Extends AutoSchema to add custom functionality for generating tags and descriptions in the OpenAPI schema.
    """
    date_example = "2021-08-31"
    datetime_example = "2021-08-31T19:24:56.830Z"
    email_example = "jane.doe@example.com"
    uri_example = "http://example.com"
    uuid_example = "123e4567-e89b-12d3-a456-426614174000"
    float_example = 1.23
    integer_example = 42
    binary_example = "SGVsbG8gV29ybGQ="  # "Hello World" em base64
    has_path_parameters = False

    def get_operation_id_base(self, path, method, action):
        """
        Override get_operation_id_base method of base class.

        Returns the operation id base for a view as defined in the view
        class attribute `operation_id_base`.
        """
        view = self.view
        if hasattr(view, 'operation_id_base') and isinstance(view.operation_id_base, str):
            return view.operation_id_base
        return super(CustomSchema, self).get_operation_id_base(path, method, action)

    def get_example(self, example):
        examples = {
            'date': "2021-08-31",
            'datetime': "2021-08-31T19:24:56.830Z",
            'email': "jane.doe@example.com",
            'uri': "http://example.com",
            'uuid': "123e4567-e89b-12d3-a456-426614174000",
            'float': 0,
            'integer': 0,
            'binary': 'binary',
            'string': 'string',
        }

        return examples.get(example)

    def map_serializer(self, serializer):
        """
        Maps the serializer by adding dynamic methods to properties.

        Args:
            serializer: The serializer mapping will be applied.

        :return:
            Fields with mapped dynamic methods.
        """
        fields = super().map_serializer(serializer)

        big_numbers = self.view.get_dynamic_methods()
        for big in big_numbers:

            example = {}
            dynamic_methods = big.bignumbermethod_set.all()
            for method in dynamic_methods:
                new_field = getattr(serializers, method.get_field_type_display())()
                big_field_type = self.map_field(new_field)['type']
                example[method.name] = big_field_type

                if big_field_type in ['object', 'array']:
                    method_fields = method.get_fields()
                    new_example = {}
                    for method_field in method_fields:
                        field_schema = self.map_field(getattr(serializers, method_field.get_field_type_display())())
                        field_type = field_schema['type']
                        format_ = field_schema.get('format')
                        if format_:
                            example_value = self.get_example(format_)
                            new_example[method_field.field] = example_value if example_value is not None else field_type
                        else:
                            example_value = self.get_example(field_type)
                            new_example[method_field.field] = example_value if example_value is not None else field_type

                    if big_field_type == 'array':
                        example[method.name] = [new_example]
                    else:
                        example[method.name] = new_example

            fields['properties'][big.path] = {
                'example': example
            }
        return fields

    def get_pagination_parameters(self, path, method):
        view = self.view
        if not view.pagination:
            return []

        paginator = self.get_paginator()
        if not paginator:
            return []

        return paginator.get_schema_operation_parameters(view)

    def get_responses(self, path, method):
        # Start main default get_responses
        if method == 'DELETE':
            return {
                '204': {
                    'description': ''
                }
            }

        self.response_media_types = self.map_renderers(path, method)

        serializer = self.get_response_serializer(path, method)

        if not isinstance(serializer, serializers.Serializer):
            item_schema = {}
        else:
            item_schema = self.get_reference(serializer)

        if is_list_view(path, method,
                        self.view) or self.view.pagination:  # Modified: Include check if is self.view.pagination
            response_schema = {
                'type': 'array',
                'items': item_schema,
            }
            paginator = self.get_paginator()
            if paginator:
                response_schema = paginator.get_paginated_response_schema(response_schema)
        else:
            response_schema = item_schema
        status_code = '201' if method == 'POST' else '200'
        # end main default get_responses

        responses = {
            status_code: {
                'content': {
                    ct: {'schema': response_schema}
                    for ct in self.response_media_types
                },
                # description is a mandatory property,
                # https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#responseObject
                # TODO: put something meaningful into it
                'description': ""
            }
        }

        custom_responses = self.view.responses
        if custom_responses:
            for code, value in custom_responses.items():
                if not responses.get(code):
                    responses[code] = {}
                responses[code]['content'] = {
                    'application/json': {
                        'example': json.loads(json.dumps(value, default=str))
                    }
                }
            for code, value in responses.copy().items():
                if code not in custom_responses:
                    responses.pop(code, None)
        return responses

    def get_kwargs_from_path(self, url_path):
        path = Path(url_path)
        kwargs = {}

        # Itera sobre cada parte do caminho do URL
        for part in path.parts:
            # Verifica se a parte começa com "{", indicando um argumento nomeado
            if part.startswith("{") and part.endswith("}"):
                # Remove as chaves "{" e "}" para obter o nome do argumento
                arg_name = part[1:-1]
                # Adiciona o argumento nomeado ao dicionário kwargs
                kwargs[arg_name] = None  # Defina o valor inicial como None ou atribua um valor padrão desejado

        return kwargs

    def get_operation(self, path, method):
        """
        Override get_operation method of base class.

        Returns the operation (HTTP method) on a path for a view method.
        Modifies the operation to include parameter descriptions.
        """
        op = super(CustomSchema, self).get_operation(path, method)
        has_path_parameters = len(self.get_kwargs_from_path(path).keys()) > 0 and not self.view.query_slug

        if method != 'GET' or has_path_parameters:
            op['parameters'] = [param for param in op['parameters'] if param['in'] == 'path']

        else:
            if not self.view.pagination:
                op['parameters'] = [param for param in op['parameters'] if param['name'] not in ('limit', 'offset')]
            else:
                op['parameters'] += self.view.default_query_params + self.view.query_params

        # Crie um conjunto para rastrear os nomes de campo já encontrados
        seen_names = set()

        # Percorra a lista de parâmetros na ordem inversa
        for count in range(len(op['parameters']) - 1, -1, -1):
            x = op['parameters'][count]
            name = x['name']

            # Verifique se o nome do campo já foi visto
            if name in seen_names:
                # Se já foi visto, remova o campo duplicado
                del op['parameters'][count]
            else:
                # Se não foi visto, adicione-o ao conjunto de nomes vistos
                seen_names.add(name)

            if x['name'] == 'ordering':
                if has_path_parameters:
                    del op['parameters'][count]
                    continue
                else:
                    op['parameters'][count][
                        'description'] = 'Campo para ordenação dos resultados. Envie uma lista com as opções escolhidas. Use o caracter - em frente a opção para descendente e apenas a opção para ascendente'
                    op['parameters'][count]['schema'] = {"type": openapi.TYPE_ARRAY,
                                                         "items": {"type": openapi.TYPE_STRING,
                                                                   "enum": self.view.ordering_fields}}

            op['parameters'][count]['description'] = str(op['parameters'][count]['description'])
            op['parameters'][count]['name'] = str(op['parameters'][count]['name'])
        return op

    def get_tags(self, path, method):
        """
        Override get_tags method of base class.

        Returns the tags for an endpoint based on the view class attributes
        `tags` or `model`.
        """
        view = self.view
        if hasattr(view, 'tags') and isinstance(view.tags, list):
            return list(map(str, view.tags))
        if view.model:
            app_label = str(view.model._meta.app_config.verbose_name.split('.')[0].capitalize())
            app = get_app_label_from_model(view.model)
            if app.lower() in app_label.lower():
                return ['{}'.format(app)]
            return ['{} - {}'.format(app, app_label)]
        return super(CustomSchema, self).get_tags(path, method)

    def map_field(self, field):
        """
        Override map_field method of base class.

        Maps a Django Rest Framework field to a dictionary representation
        as required by OpenAPI 3.0.0 spec.
        """
        if isinstance(field, CustomDictField):
            return {
                'type': 'any',
            }
        return super(CustomSchema, self).map_field(field)

    def get_description(self, path, method):
        """
        Override get_description method of base class.

        Returns the description for an endpoint as defined in the view method's
        docstring or in the view class attribute `docs`.
        """
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

        return formatting.dedent(smart_str(init + '\n\n' + str(docstring)))

    def _get_init_description(self) -> str:
        """Helper method for getting initial description for an endpoint."""
        view = self.view
        if hasattr(view, 'docs') and isinstance(view.docs, dict) and view.docs.get('init'):
            return view.docs.get('init')
        return ''


class SimpleFilterBackend(BaseFilterBackend, ABC):

    @staticmethod
    def get_schema_operation_parameters(view):
        """
        Returns the query parameters for the schema operation.

        Args:
            view: The view obtaining the query parameters.

        Returns:
            Query parameters.
        """
        return view.query_params


class CustomLimitOffsetPagination(LimitOffsetPagination):
    max_limit = 30

    def paginate_queryset_ids(self, queryset, request, view=None):
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None

        self.count = self.get_count(queryset)
        self.offset = self.get_offset(request)
        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []
        return list(queryset[self.offset:self.offset + self.limit].values_list('id', flat=True))


class AbstractViewApi(generics.GenericAPIView, OrderingFilter):
    """HTTP methods for Api VIew"""
    filter_backends = (SimpleFilterBackend, OrderingFilter)
    permission_classes = [CheckAPIVersion]
    query_params = []
    pagination_class = None
    pagination = False
    responses = None
    order_by = True
    ordering_fields = []  # Especifique quais campos podem ser usados para ordenação
    default_ordering_fields = ['created_at',
                               'updated_at']  # Especifique quais campos padrões podem ser usados para ordenação

    # ordering = ['created_at'] # Especifique os campos que serão usados para ordenação

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ordering_fields = self.get_ordering_fields()
        if self.pagination:
            self.pagination_class = CustomLimitOffsetPagination

    def get_ordering_fields(self):

        if not self.order_by:
            return []
        ordering_fields = self.get_default_ordering_fields()
        ordering_fields.extend(self.get_non_relation_fields())
        ordering = ordering_fields + self.ordering_fields.copy()
        ordering_hifen = []

        for s in ordering:
            ordering_hifen.append(f"-{s}")
        ordering.extend(ordering_hifen)

        return ordering

    def get_default_ordering_fields(self):
        return ['created_at', 'updated_at']

    default_query_params = [
        {
            "name": "created_at_min",
            "field": "created_at__gte",
            "in": "query",
            "required": False,
            "description": str(_("Created at start")),
            "schema": {"type": "date"}
        },
        {
            "name": "created_at_max",
            "field": "created_at__lte",
            "in": "query",
            "required": False,
            "description": str(_("Created at end")),
            "schema": {"type": "date"}
        },
        {
            "name": "updated_at_min",
            "field": "updated_at__gte",
            "in": "query",
            "required": False,
            "description": str(_("Updated at start")),
            "schema": {"type": "date"}
        },
        {
            "name": "updated_at_max",
            "field": "updated_at__lte",
            "in": "query",
            "required": False,
            "description": str(_("Updated at end")),
            "schema": {"type": "date"}
        }
    ]
    model = None
    schema = CustomSchema()
    cache_timeout = 60 * 60 * 24
    cache_version = 'v1'
    allow_cache: bool = True
    allowed_versions = ['v1']
    query_slug = False
    many = True

    def get_non_relation_fields(self):
        non_relation_fields = []

        if not self.model:
            return non_relation_fields

        for field in self.model._meta.fields:
            if not isinstance(field, (models.ForeignKey, models.OneToOneField, models.ManyToManyField)):
                non_relation_fields.append(field.name)
        return list(set(non_relation_fields))

    # def get_permissions(self):
    #     """
    #     Instantiates, append CheckAPIVersion and returns the list of permissions that this view requires.
    #     """
    #     permissions = super().get_permissions()
    #
    #     # Adicione suas permissões personalizadas aqui
    #     permissions.append(CheckAPIVersion())
    #
    #     return permissions
    def get_dynamic_methods(self) -> list:
        """
        Returns a list of dynamic methods to be added as properties to the serializer.

        :return:
            List of dynamic methods.
        """
        return []

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the HTTP request method.

        :return:
            Serializer class.
        """
        if hasattr(self, 'layout_serializers'):
            return self.layout_serializers.get(self.request.method.lower(), self.layout_serializers['default'])
        return super(AbstractViewApi, self).get_serializer_class()

    @staticmethod
    def get_schema_operation_parameters(view):
        """
        Returns the query parameters for the schema operation.

        Args:
            view: The view obtaining the query parameters.

        :return:
            Query parameters.
        """
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

    def get_query_parameters(self):
        query = {}

        valid_parameters = self.query_params + self.default_query_params
        for valid_params in valid_parameters:
            type_instance = valid_params['schema']['type']
            field = valid_params['field']
            name = valid_params['name']
            value = self.request.query_params.get(name)
            if value:
                instance = self.__get_type_by_instance(type_instance)
                try:
                    value = instance['parser'](value)
                except (ValueError, KeyError):
                    pass
                if isinstance(value, instance['type']):
                    query[field] = value
                else:
                    raise serializers.ValidationError(
                        {name: _('Field in invalid format. It must be in the format{}').format(instance["legend"])})
        return query

    def filter(self, id_, **kwargs):
        query = self.get_queryset()
        get_query_slug = self.get_query_slug()
        query.update(get_query_slug)
        query_exclude = self.get_exclude_queryset()
        query_parameters = self.get_query_parameters()
        query.update(query_parameters)
        query.update(kwargs)

        if id_ or self.many is False:
            if id_:
                query['id'] = id_
            obj = self.model.objects.exclude(**query_exclude).filter(**query).first()
            if not obj:
                raise Http404
            return obj

        queryset = self.model.objects.exclude(**query_exclude).filter(**query).distinct()
        ordering = self.get_ordering(self.request, queryset, self)
        if ordering:
            return queryset.order_by(*ordering)
        return queryset

    def get_ordering(self, request, queryset, view):
        """
        Ordering is set by a comma delimited ?ordering=... query parameter.

        The `ordering` query parameter can be overridden by setting
        the `ordering_param` value on the OrderingFilter or by
        specifying an `ORDERING_PARAM` value in the API settings.
        """
        params = request.query_params.getlist(self.ordering_param)
        if params:
            fields = params
            ordering = self.remove_invalid_fields(queryset, fields, view, request)
            if ordering:
                return ordering

        # No ordering was included, or all the ordering fields were invalid
        return self.get_default_ordering(view)

    def get_query(self, id_=None, **kwargs):
        """Validate parameters received in query params, returning query values"""

        obj = self.filter(id_, **kwargs)

        many = False if id_ or self.many is False else True
        return self.serializer(obj, many)

    def get_cache_key(self, request):
        """Generates a unique cache key for the current request and model."""
        app_label = self.model._meta.verbose_name.lower().replace(' ', '_')
        url = request.build_absolute_uri()
        app_name = get_app_label_from_model(self.model).replace(' ', '_')
        cache_key = make_template_fragment_key(app_label, [url])
        user_key = request.user.id
        return f'{self.cache_version}:{app_name}:{app_label}:{cache_key}:{user_key}'

    def __get_keys(self):
        """Helper method to get a list of all existing cache keys."""
        return cache.get(f"{self.cache_version}:keys", [])

    def __set_key(self, key, value, timeout: float = 60 * 60 * 24):
        """Helper method to set a new cache key with a given value and timeout."""
        keys_list = self.__get_keys()
        if key not in keys_list:
            keys_list.append(key)
            cache.set(f"{self.cache_version}:keys", keys_list)
        cache.set(key, value, timeout)

    def __delete_key(self, key):
        """Helper method to delete a cache key and remove it from the list of existing keys."""
        keys_list = self.__get_keys()
        if key in keys_list:
            keys_list.remove(key)
            cache.delete(key)
            cache.set(f"{self.cache_version}:keys", keys_list)

    def get_cache_keys_from_app(self, model):
        """Returns a list of cache keys for a given app name (model label)."""
        keys = self.__get_keys()
        app_name = get_app_label_from_model(model)
        url_keys = []
        for key in keys:
            if key.startswith(f'{self.cache_version}:{app_name}'):
                url_keys.append(key)
        return url_keys

    def get_cache_keys_from_user(self):
        """Returns a list of cache keys for a given user request."""
        keys = self.__get_keys()
        url_keys = []
        for key in keys:
            key_label = key.split(':')
            if str(self.request.user.id) in key_label[-1]:
                url_keys.append(key)
        return url_keys

    def get_cache_keys_from_labels(self, app_labels: list):
        """Returns a list of cache keys for all apps in a given list of app labels."""
        keys = self.__get_keys()
        url_keys = []
        for key in keys:
            key_label = key.split(':')
            if key_label[2] in app_labels:
                url_keys.append(key)
        return url_keys

    def delete_cache_from_app(self, model):
        """Deletes all cache keys associated with a given app/model"""
        url_keys = self.get_cache_keys_from_app(model)
        for key in url_keys:
            self.__delete_key(key)

    def delete_cache_from_user(self):
        """Deletes all cache keys associated with a given request user"""
        url_keys = self.get_cache_keys_from_user()
        for key in url_keys:
            self.__delete_key(key)

    def delete_cache_from_labels(self):
        """Deletes all cache keys associated with a list of app labels."""
        labels = ['project', 'creditor', 'calculation']
        url_keys = self.get_cache_keys_from_labels(labels)
        for key in url_keys:
            self.__delete_key(key)

    def dispatch(self, request, *args, **kwargs):
        """
        Overrides the default dispatch method to handle caching. If a GET request has a cached response,
        it returns the cached response. When a model instance is created, updated, or deleted, it deletes all cached
        responses for related models and app instances.
        """
        # TODO fazer referencia da key para um elm, para nao precisar apagar todos os apps relacionados
        if not self.model or not self.allow_cache or not ENABLE_CACHE:
            return super().dispatch(request, *args, **kwargs)
        fernet = Security()
        cache_key = self.get_cache_key(request)
        if request.method == 'GET':
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return JsonResponse(json.loads(fernet.decrypt(cached_data)), safe=False)

        response = super().dispatch(request, *args, **kwargs)
        if response.status_code in [200, 201] and request.method == 'GET':
            try:
                self.__set_key(cache_key, fernet.encrypt(response.content.decode()))
            except ContentNotRenderedError:
                pass

        if request.method != 'GET':
            self.delete_cache_from_app(self.model)
            related_serializers = find_related_serializers(self.get_serializer_class())
            for serializer_cls in related_serializers:
                model_class = serializer_cls.Meta.model
                self.delete_cache_from_app(model_class)
        return response

    def get_query_slug(self):
        if self.query_slug:
            resolver_match = resolve(self.request.path_info)
            return resolver_match.kwargs
        return {}

    def serializer(self, obj, many):
        exclude = self.get_exclude_queryset()
        serializer = self.get_serializer_class()
        return serializer(obj, many=many, exclude=exclude, context={'request': self.request}).data

    def get(self, request, *args, **kwargs):
        """Abstract method for default method GET. Override method in class for custom operation"""
        id_ = kwargs.get('id')

        if self.pagination:
            queryset = self.filter(id_, **kwargs)

            paginated_queryset = self.paginate_queryset(queryset)
            data = self.serializer(paginated_queryset, many=True)
            return self.get_paginated_response(data)

        query = self.get_query(id_=id_)
        return JsonResponse(query, safe=False)

    def post(self, request, *args, **kwargs):
        """Abstract method for default method POST. Override method in class for custom operation"""
        with transaction.atomic():
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            new_obj = serializer.validated_data
            obj = self.model.objects.create(**new_obj)
        return JsonResponse({self.get_model_name(): self.serializer_class(obj, many=False).data},
                            status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        """
        This method handles PUT requests for the view. It expects input data that conform to the serializer used by
        the view class. It updates the approved_calculation or date object of a specific comparative object using the
        given calculation_id from the query parameters and serializes the updated object in JSON format before
        returning it as an HTTP response.

        :params:
            request: The HTTP request object. args: Any additional positional arguments passed to the method.
        kwargs: Any additional keyword arguments passed to the method, with calculation_id identifying the
        comparative object to update. :return: JsonResponse: An HTTP response containing the updated and serialized
        comparative object data.
        """
        with transaction.atomic():
            id_ = kwargs.get('id')
            exclude = self.__get_exclude_values()
            serializer = self.get_serializer_class()

            obj = get_object_or_404(self.model, id=id_)

            try:
                serializer = serializer(instance=obj, data=request.data, exclude=exclude)
            except ValueError:
                serializer = serializer(instance=obj, data=request.data)

            serializer.is_valid(raise_exception=True)
            data_obj = serializer.validated_data

            for field_name in serializer.fields:
                field = serializer.fields[field_name]
                if isinstance(field, serializers.ManyRelatedField):
                    values = data_obj.pop(field_name, False)
                    if isinstance(values, list):
                        attr = getattr(obj, field_name)
                        attr.clear()
                        attr.add(*values)
            serializer.save()
        return JsonResponse({self.get_model_name(): self.serializer_class(obj, many=False).data})

    def get_model_name(self):
        """Helper method to get app_label."""
        return self.model._meta.verbose_name.lower().replace(' ', '_')

    def delete(self, request, *args, **kwargs):
        """Abstract method for default method DELETE. Override method in class for custom operation"""
        obj_id = kwargs.get('id')
        obj = get_object_or_404(self.model, id=obj_id)
        obj.delete()
        return JsonResponse({'data': _(f'{self.get_model_name().replace("_", " ").title()} deleted')},
                            status=status.HTTP_200_OK)

    def __get_exclude_values(self) -> list or tuple:
        if hasattr(self, 'exclude') and (isinstance(self.exclude, list) or isinstance(self.exclude, tuple)):
            return self.exclude
        return []

    def get_queryset(self):
        """Helper method for getting filter queryset."""
        return {}

    def get_exclude_queryset(self):
        """Helper method for getting filter queryset to remove."""
        return {}


# Get all Schemas
model_serializer_subclasses = []
for app in apps.get_app_configs():
    schema_path = os.path.join(app.path, "schemas.py")
    if os.path.exists(schema_path):
        spec = spec_from_file_location(f"{app.name}.schemas", schema_path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        members = inspect.getmembers(module)
        for member_name, member in members:
            if inspect.isclass(member) and (
                    issubclass(member, serializers.ModelSerializer) or issubclass(member,
                                                                                  AbstractDescriptionSchema)):
                model_serializer_subclasses.append(member)


def find_related_serializers(schema, checked_serializers=None):
    """
    Find all model serializer subclasses and their related serializers by schema.

    model_serializer_subclasses - list of model serializer subclasses found in schemas.py files in each app's
    directory. find_related_serializers - recursively finds related serializers for a given schema by searching the
    fields of each model serializer subclass. @param schema: The schema class to search for related serializers by.
    @return: A list of model serializer classes that are related to the given schema class.
    """

    related_serializer_schemas = []
    if checked_serializers is None:
        checked_serializers = set()
    checked_serializers.add(schema)

    def append_srl(srl):
        if not srl in related_serializer_schemas:
            related_serializer_schemas.append(srl)

    for serializer_cls in model_serializer_subclasses:
        try:
            for field_name, field in serializer_cls().get_fields().items():
                if str(field.__class__.__name__).endswith('Schema'):
                    if field.__class__.__name__ == schema.__name__:
                        append_srl(serializer_cls)
                elif isinstance(field, serializers.ListSerializer):
                    if field.child.__class__.__name__ == schema.__name__:
                        append_srl(serializer_cls)
                elif isinstance(field, serializers.Serializer):
                    if field.__class__ == schema.__name__:
                        append_srl(serializer_cls)
        except ValueError:
            pass

    for serializer_cls in related_serializer_schemas:
        if serializer_cls not in checked_serializers:
            related_serializer_schemas.extend(
                find_related_serializers(serializer_cls, checked_serializers))
    return related_serializer_schemas
