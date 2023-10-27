from django.core.management.base import BaseCommand

from rates.commands import SetAccumulated
from rates.models import Rate


class Command(BaseCommand):
    help = 'Calcule accumulated and period value for rates when initial_accumulated'

    def handle(self, *args, **options):
        rates = Rate.objects.filter(initial_accumulated__isnull=False)

        for rate in rates:
            SetAccumulated(rate_id=rate.id).update_rate()
