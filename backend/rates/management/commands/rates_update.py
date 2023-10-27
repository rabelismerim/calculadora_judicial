from django.core.management.base import BaseCommand

from rates.commands import AutomaticUpdateRates
from rates.models import Rate


class Command(BaseCommand):
    help = 'Update rates values'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Force the rate update all available dates')

    def handle(self, *args, **options):
        rates = Rate.objects.filter(initial_accumulated__isnull=False)

        for rate in rates:
            force_update = options['force']
            AutomaticUpdateRates(rate_id=rate.id, force=force_update).update_rate()
