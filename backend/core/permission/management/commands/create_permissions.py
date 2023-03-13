from django.core.management.base import BaseCommand
from django.apps import apps as default_apps
from django.conf import settings
from django.contrib.auth.models import Permission, Group

from core.permission.views import CreatePermissions


class Command(BaseCommand):
    help = 'run create permissions group'

    def print_start(self, msg):
        self.stdout.write(self.style.SUCCESS(msg))

    def create_update_permissions(self):
        """
        Create or update permissions Groups
        """
        project_manager_list, created, id_ = CreatePermissions().create_project_manager()
        self.print_start(
            f'Successfully {"created" if created else "altered"} group\nNumber of permissions: {len(project_manager_list)}')

    def handle(self, *args, **options):
        self.create_update_permissions()
