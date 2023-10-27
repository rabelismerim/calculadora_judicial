import json
import os
from django.core.management.base import BaseCommand

from rates.commands import SetAccumulated
from rates.models import Rate, RateValues, Accumulated, Period


def create_indices():
    """Create Index by files"""
    base = 'rates/indices'
    for file in os.listdir(base):

        with open(f'{base}/{file}', 'r', encoding='utf-8') as f:
            index = json.loads(f.read())
        index_name = index.get('index')
        is_per_day = index.get('is_per_day')
        rows = index.get('values')
        initial_accumulated = index.get('initial_accumulated')
        code = index.get('code')

        cont = 0

        if code:
            new_rate, created = Rate.objects.update_or_create(code=code, defaults={
                'is_per_day': is_per_day,
                'initial_accumulated': initial_accumulated,
                'index': index_name
            })
        else:
            new_rate, created = Rate.objects.update_or_create(index=index_name, defaults={
                'is_per_day': is_per_day,
                'initial_accumulated': initial_accumulated
            })

        rates = Rate.objects.filter(index=index_name)
        print(index_name, 'index\n\n')
        rate_values_list = []
        accumulated_values_list = []
        period_values_list = []
        for data in rows:
            accumulated = data.get('accumulated', None)
            period = data.get('period', None)
            date = data.get('date')
            value = data.get('value')

            if rates.filter(ratevalues__date=date).exists():
                continue

            rate_value = RateValues(rate=new_rate, date=date, value=value)
            rate_values_list.append(rate_value)
            cont += 1
            if accumulated is not None:
                accumulated = Accumulated(rate_id=rate_value.id, value=accumulated)
                accumulated_values_list.append(accumulated)
            if period is not None:
                period = Period(rate_id=rate_value.id, value=period)
                period_values_list.append(period)
        RateValues.objects.bulk_create(rate_values_list)
        Accumulated.objects.bulk_create(accumulated_values_list)
        Period.objects.bulk_create(period_values_list)

        SetAccumulated(rate_id=new_rate.id).update_rate()
        print(f'\033[92m Successful {"created" if created else "altered"} {index_name}\n Total: {cont}')


class Command(BaseCommand):
    help = 'Create Indicies values by json file'

    def handle(self, *args, **options):
        create_indices()
