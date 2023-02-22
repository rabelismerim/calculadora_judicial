from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions, serializers, status
from rates.models import Rate, RateFile
from rates.schemas import RateFileSchema, RateSchema


class RateApi(AbstractViewApi):
    """HTTP methods for Rate"""
    http_method_names = ['post', 'get']
    serializer_class = RateSchema
    permission_classes = [permissions.IsAdminUser]
    model = Rate
    schema = AutoSchema(tags=["Rate"], component_name='teste')

    query_params = [
        {
            "name": "valor",
            "field": "value__icontains",
            "in": "query",
            "required": False,
            "description": "Valor",
            "schema": {"type": "string"}
        }
    ]

    def post(self, request, *args, **kwargs):
        """Abstract method for default get model. Overide method in class for custom operation"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_rate = serializer.validated_data
        return JsonResponse({'rate': self.serializer_class(new_rate, many=False).data}, status=status.HTTP_201_CREATED)


class RateFileApi(AbstractViewApi):
    """HTTP methods for rate_file"""
    http_method_names = ['post', 'get']
    serializer_class = RateFileSchema
    permission_classes = [permissions.AllowAny]
    # permission_classes = [permissions.IsAdminUser]
    model = Rate
    schema = AutoSchema(tags=["RateFile"])

    query_params = [
        {
            "name": "valor",
            "field": "value__icontains",
            "in": "query",
            "required": False,
            "description": "Valor",
            "schema": {"type": "string"}
        }
    ]

    def post(self, request, *args, **kwargs):
        """Abstract method for default get model. Overide method in class for custom operation"""
        data = request.data
        file = request.FILES.get('file')
        index_name = data.get('index')

        if not index_name:
            raise serializers.ValidationError(['Necessário o campo: index'])

        if not file:
            raise serializers.ValidationError(['Necessário o campo: file'])

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

        if rows == False:
            raise serializers.ValidationError(
                [f'O arquivo {filename} não contêm os campos corretos. Necessário ao menos a coluna mes e indice, acumulado e periodo são opcionais'])

        if len(rows) == 0:
            raise serializers.ValidationError(
                [f'O arquivo {filename} está vazio'])

        for new_rate in rows:
            serializer = RateSchema(data=new_rate)
            serializer.is_valid(raise_exception=False)

        return JsonResponse({'rate': RateSchema(new_index, many=False).data}, status=status.HTTP_201_CREATED)
