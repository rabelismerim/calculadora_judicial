import json
import os
from django.core.management.base import BaseCommand

from rates.commands import SetAccumulated, AutomaticUpdateRates
from rates.models import Rate


def create_indices():
    """Create Index by files"""
    base = 'rates/indices_ok'

    averages = []
    for file in os.listdir(base):

        with open(f'{base}/{file}', 'r', encoding='utf-8') as f:
            index = json.loads(f.read())
        index_name = index.get('index')
        is_per_day = index.get('is_per_day')
        initial_accumulated = index.get('initial_accumulated')
        code = index.get('code')
        start_indice = index.get('start_indice')
        average = index.get('average', [])

        cont = 0

        if code:
            new_rate, created = Rate.objects.update_or_create(code=code, defaults={
                'is_per_day': is_per_day,
                'initial_accumulated': initial_accumulated,
                'index': index_name,
                'start_indice': start_indice
            })
        else:
            new_rate, created = Rate.objects.update_or_create(index=index_name, defaults={
                'is_per_day': is_per_day,
                'initial_accumulated': initial_accumulated,
                'start_indice': start_indice
            })

        if average:
            averages.append((new_rate, average))

        AutomaticUpdateRates(rate_id=new_rate.id, force=True).update_rate()

        print(f'\033[92m Successful {"created" if created else "altered"} {index_name}\n Total: {cont}')

    for rate, average in averages:
        rates = Rate.objects.filter(index__in=average)
        rate.average.add(*rates)
        SetAccumulated(rate_id=rate.id).update_average()

    print(f'\033[92m Successful')


class Command(BaseCommand):
    help = 'Create Indicies values by json file, getting rate values in Bacen'

    def handle(self, *args, **options):
        create_indices()
