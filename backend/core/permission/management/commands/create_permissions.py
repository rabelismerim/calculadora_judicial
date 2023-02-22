from django.core.management.base import BaseCommand
from django.apps import apps as default_apps
from django.conf import settings
from django.contrib.auth.models import Permission, Group


class Command(BaseCommand):
    help = 'run create permissions group'

    def print_start(self, msg):
        self.stdout.write(self.style.SUCCESS(msg))

    def create_update_permissions(self):
        """
        Create or update permissions Groups
        """
        project_manager_list = []

        create_group = {'name': 'Project Manager'}
        group_manager, created = Group.objects.get_or_create(
            defaults=create_group, **create_group)

        apps = []
        for app in settings.INSTALLED_APPS:  # Get models
            app_name = app.split('.')
            if len(app_name) > 1:  # Apps private
                app_lbl = app_name[0]
                model_name = app_name[1]
                app_models = default_apps.all_models[model_name]
                if app_models:
                    apps.append((app_lbl, app_models))

        for label, app in apps:  # Get permissions in apps
            for model in app.values():
                permissions_app = Permission.objects.filter(
                    content_type__app_label=model._meta.app_label, content_type__model=model._meta.model_name)
                if label == 'projects':  # List permissions to Project Manager group
                    project_manager_list.extend(permissions_app)

        group_manager.permissions.add(*project_manager_list)
        self.print_start(
            f'Successfully {"created" if created else "altered"} group\nNumber of permissions: {len(project_manager_list)}')

    def handle(self, *args, **options):
        self.create_update_permissions()
