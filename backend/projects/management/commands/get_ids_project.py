# create_data.py
import json
import random
from django.core.management.base import BaseCommand

from projects.create_project import get_data_project
from utils import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Get data ids to projetct.'

    def handle(self, *args, **options):
        data = get_data_project()

        with open('project_ids.json', 'w') as f:
            f.write(json.dumps(data))
