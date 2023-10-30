from django.core.management.base import BaseCommand

from rates.commands import SetAccumulated, AutomaticUpdateRates
from rates.models import Rate


class Command(BaseCommand):
    help = 'Calcule accumulated and period value for rates when initial_accumulated'

    def handle(self, *args, **options):
        rates = Rate.objects.filter(initial_accumulated__isnull=False, code__gte=1)

        for rate in rates:
            SetAccumulated(rate_id=rate.id).update_rate()

        rates = Rate.objects.filter(start_indice__isnull=False)

        for rate in rates:
            SetAccumulated(rate_id=rate.id).update_average()
