import datetime
import inspect
import json
import os
from abc import ABC
from importlib.util import spec_from_file_location, module_from_spec

from django.apps import apps
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.http import JsonResponse, Http404
from django.template.response import ContentNotRenderedError
from django.utils.encoding import smart_str
from drf_yasg import openapi
from rest_framework import generics, serializers, status
from rest_framework.filters import BaseFilterBackend
from rest_framework.generics import get_object_or_404
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

        Returns:
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

    def get_operation(self, path, method):
        """
        Override get_operation method of base class.

        Returns the operation (HTTP method) on a path for a view method.
        Modifies the operation to include parameter descriptions.
        """
        op = super(CustomSchema, self).get_operation(path, method)
        op['parameters'] = list(map(lambda x: {**x, 'description': str(x['description'])}, op['parameters']))
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
    def get_schema_operation_parameters(self, view):
        return view.query_params


class AbstractViewApi(generics.GenericAPIView):
    """HTTP methods for Api VIew"""
    filter_backends = (SimpleFilterBackend,)
    permission_classes = [CheckAPIVersion]
    query_params = []
    model = None
    schema = CustomSchema()
    cache_timeout = 60 * 60 * 24
    cache_version = 'v1'
    allow_cache: bool = True
    allowed_versions = ['v1']

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

        Returns:
            List of dynamic methods.
        """
        return []

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the HTTP request method.

        Returns:
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

        Returns:
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

    def get_query(self, id_=None, **kwargs):
        """Validate parameters received in query params, returning query values"""
        query = self.get_queryset()
        query_exclude = self.get_exclude_queryset()
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
                except (ValueError, KeyError):
                    pass
                if isinstance(value, instance['type']):
                    query[field] = value
                else:
                    raise serializers.ValidationError(
                        {name: _('Field in invalid format. It must be in the format{}').format(instance["legend"])})
        serializer = self.get_serializer_class()
        if id_:
            obj = self.model.objects.exclude(**query_exclude).filter(id=id_, **query, **kwargs).first()
            if not obj:
                raise Http404
            return serializer(obj, many=False, exclude=exclude).data
        return serializer(self.model.objects.exclude(**query_exclude).filter(**query, **kwargs).distinct(), many=True,
                          exclude=exclude).data

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

    def get(self, request, *args, **kwargs):
        """Abstract method for default method GET. Override method in class for custom operation"""
        id_ = kwargs.get('id')
        query = self.get_query(id_=id_)
        model_name = self.model._meta.verbose_name_plural.lower() if not id_ else self.__get_model_name()
        return JsonResponse({model_name.replace(' ', '_'): query})

    def post(self, request, *args, **kwargs):
        """Abstract method for default method POST. Override method in class for custom operation"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_obj = serializer.validated_data
        obj = self.model.objects.create(**new_obj)
        return JsonResponse({self.__get_model_name(): self.serializer_class(obj, many=False).data},
                            status=status.HTTP_201_CREATED)

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
        serializer = self.get_serializer_class()
        try:
            serializer = serializer(data=request.data, exclude=exclude)
        except ValueError:
            serializer = serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data_obj = dict(serializer.validated_data)
        obj = get_object_or_404(self.model, id=id_)
        obj.dict_update(**data_obj)
        return JsonResponse({self.__get_model_name(): self.serializer_class(obj, many=False).data})

    def __get_model_name(self):
        """Helper method to get app_label."""
        return self.model._meta.verbose_name.lower().replace(' ', '_')

    def delete(self, request, *args, **kwargs):
        """Abstract method for default method DELETE. Override method in class for custom operation"""
        obj_id = kwargs.get('id')
        obj = get_object_or_404(self.model, id=obj_id)
        obj.delete()
        return JsonResponse({'data': _(f'{self.__get_model_name().capitalize()} deleted')}, status=status.HTTP_200_OK)

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
