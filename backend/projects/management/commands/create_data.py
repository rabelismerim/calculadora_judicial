# create_data.py
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from faker import Faker

from core.utils.progress_bar import progressbar

from projects.judge.models import Judge
from projects.court.models import Court
from projects.lawyer.models import Lawyer
from projects.region.models import Region

fake = Faker()


def get_description():
    name = fake.name()
    data = dict(
        description=name,
    )
    return data


def create_fake(modelby, number, description):
    aux_list = []
    for _ in progressbar(range(number), description):
        data = get_description()
        obj = modelby(**data)
        aux_list.append(obj)
    modelby.objects.bulk_create(aux_list)


class Command(BaseCommand):
    help = 'Create data.'

    def handle(self, *args, **options):
        create_fake(Judge, 30, 'Juiz')
        create_fake(Court, 30, 'Corte')
        create_fake(Lawyer, 30, 'Advogados')
        create_fake(Region, 30, 'Regioes')
