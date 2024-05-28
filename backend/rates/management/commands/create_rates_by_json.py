import datetime
import json
import logging
import os
from django.core.management.base import BaseCommand

from rates.models import Rate, Source, Unit


class Date:
    def __init__(self, date):
        if not date:
            self.date = None
        else:
            try:
                date_obj = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
            self.date = date_obj.strftime('%Y-%m-%d')


def create_indices():
    """Create Index by files"""
    base = 'rates/rate'
    url = 'https://www3.bcb.gov.br/sgspub/localizarseries/localizarSeries.do?method=prepararTelaLocalizarSeries'
    for file in os.listdir(base):
        index_name = file
        with open(f'{base}/{file}', 'r', encoding='utf-8') as f:
            rows = json.loads(f.read())

        rates = Rate.objects.all()
        sources = Source.objects.all()
        units = Unit.objects.all()

        rates_bulk = []
        sources_bulk = []
        units_bulk = []
        for row in rows:
            unit_descript = row.get("unidade")
            source_descript = row.get("fonte")
            code = row.get("codigo")
            periodicity = row.get("periodicidade")
            start_date = row.get("data_inicio")
            end_date = row.get("data_do_ultimo_valor_da_serie")

            is_per_day = periodicity.upper() == 'D'
            start_date = Date(start_date).date
            end_date = Date(end_date).date
            description =  row.get("nome_completo")
            obj = {'code': code, 'description': description, 'start_date': start_date, 'index': description,
                   'end_date': end_date, 'periodicity': periodicity, 'is_active': False, 'is_auto_update': True,
                   'is_per_day': is_per_day}
            new_rate = rates.filter(code=code).first()
            created = False
            if not new_rate:
                new_rate = Rate(**obj)
                created = True
            else:
                new_rate.dict_update(**obj)

            source = sources.filter(description=source_descript, url=url).first()
            if not source:
                source = Source(description=source_descript, url=url)
                sources_bulk.append(source)
            new_rate.source = source
            unit = units.filter(description=unit_descript).first()
            if not unit:
                unit = Unit(description=unit_descript)
                units_bulk.append(unit)
            new_rate.unit = unit
            if created:
                rates_bulk.append(new_rate)
            else:
                new_rate.dict_update(**new_rate.__dict__)

        Source.objects.bulk_create(sources_bulk)
        Unit.objects.bulk_create(units_bulk)
        Rate.objects.bulk_create(rates_bulk)
        logging.info(f'\033[92m Successful "created" {index_name}\n Total: {len(rates_bulk)}')


class Command(BaseCommand):
    help = 'Create Indicies values by json file'

    def handle(self, *args, **options):
        create_indices()
