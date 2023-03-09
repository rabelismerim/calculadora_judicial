import datetime
from django.http import JsonResponse
from rest_framework import generics, serializers, status
from rest_framework.filters import BaseFilterBackend


class SimpleFilterBackend(BaseFilterBackend):
    def get_schema_operation_parameters(self, view):
        return view.query_params


class AbstractViewApi(generics.GenericAPIView):
    """HTTP methods for Student"""
    filter_backends = (SimpleFilterBackend,)
    query_params = []

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
        exclude = []

        if hasattr(self, 'exclude') and (isinstance(self.exclude, list) or isinstance(self.exclude, tuple)):
            exclude = self.exclude

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
                        {name: f'Campo no formato inválido. Deve ser estar no formato {instance["legend"]}'})
        serializer = self.get_serializer_class()
        if id_:
            return serializer(self.model.objects.filter(id=id_, **query, **kwargs).first(), many=False, exclude=exclude).data
        return serializer(self.model.objects.filter(**query, **kwargs), many=True, exclude=exclude).data

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
        obj_name = self.model._meta.verbose_name_plural.lower(
        )
        return JsonResponse({obj_name: self.serializer_class(obj, many=False).data}, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return {}
