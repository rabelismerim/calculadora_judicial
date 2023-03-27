from django.core.management.base import BaseCommand
from core.permission.views import CreatePermissions


class Command(BaseCommand):
    help = 'run create permissions group'

    def print_start(self, msg):
        self.stdout.write(self.style.SUCCESS(msg))

    def create_update_permissions(self):
        """
        Create or update permissions Groups
        """
        group_names = ['all_groups', 'approve', 'reviewer', 'executor', 'special_approve']
        for group_name in group_names:
            project_manager_list, created, id_ = CreatePermissions().create_group_by_name(group_name)

            self.print_start(
                f'Successfully {"created" if created else "altered"} group {group_name}\nNumber of permissions: '
                f'{len(project_manager_list)}')

    def handle(self, *args, **options):
        self.create_update_permissions()
