from django.contrib import admin, messages
from django.contrib import admin, messages
from rates.models import Accumulated, Period, Rate, RateValues, RateFile
from rates.schemas import RateSchema

admin.site.register(Accumulated)
admin.site.register(Period)
admin.site.register(Rate)
admin.site.register(RateValues)


def load_files(modeladmin, request, queryset):
    for obj in queryset:
        rows = obj.get_excel_to_dict()

        if rows == False:
            messages.error(
                request, f'O arquivo {obj.filename} não contêm os campos corretos. Necessário ao menos a coluna mes e indice, acumulado e periodo são opcionais')
            continue

        if len(rows) == 0:
            continue

        cont = 0
        for new_rate in rows:
            serializer = RateSchema(data=new_rate)
            is_valid = serializer.is_valid(raise_exception=False)
            new_rate = serializer.validated_data
            if is_valid:
                cont += 1
        if cont > 0:
            messages.success(
                request, f'Carregado {cont} indice(s) do arquivo {obj.filename}')
        else:
            messages.warning(
                request, f'Nenhum indice carregado do arquivo {obj.filename}')


class CustomRateFile(admin.ModelAdmin):
    actions = [load_files]


admin.site.register(RateFile, CustomRateFile)
