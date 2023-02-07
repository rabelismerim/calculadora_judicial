import datetime
from rest_framework import generics, serializers, permissions
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
        """Parse sting to date"""
        return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()

    @staticmethod
    def __parse_datetime(date_string):
        """Parse sting to datetime"""
        return datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M')

    def __get_type_by_instance(self, instance):
        """Get instance, type, parser and legend by field schema type"""
        types = {
            'string': {'type': str, 'parser': str, 'legend': 'string'},
            'date': {'type': datetime.date, 'parser': self.__parse_date, 'legend': '2001-12-30'},
            'datetime': {'type': datetime.date, 'parser': self.__parse_datetime, 'legend': '2001-12-30 23:01'},
            'float': {'type': float, 'parser': float, 'legend': '01.00'},
            'int': {'type': int, 'parser': int, 'legend': '1'},
        }

        return types.get(instance, str)

    def get_query(self):
        """Validate parameters received in query params, returning query values"""
        query = {}
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
        data = self.model.objects.filter(**query)
        return self.serializer_class(data, many=True).data
