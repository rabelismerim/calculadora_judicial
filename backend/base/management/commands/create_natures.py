import logging

from django.core.management.base import BaseCommand
from base.models import NatureChoice, NATURES


def create_natures():
    natures = NATURES
    list_natures = NatureChoice.objects.all()
    natures_bulk = []
    for nature_en, nature_pt in natures:
        if not list_natures.filter(description=nature_en).exists():
            new_nature = NatureChoice(description=nature_en, description_en=nature_en, description_pt_br=nature_pt)
            natures_bulk.append(new_nature)

    NatureChoice.objects.bulk_create(natures_bulk)
    logging.info(f'\033[92m Successful "created" natures \n Total: {len(natures_bulk)}')


class Command(BaseCommand):
    help = 'Create nature choices for Creditor'

    def handle(self, *args, **options):
        create_natures()
