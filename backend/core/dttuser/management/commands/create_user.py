from django.core.management.base import BaseCommand

from config.settings import ENABLE_SSO, PASSWD_DEV
from core.permission.views import CreatePermissions
from utils import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'run create user dev and admin'

    def print(self, msg):
        self.stdout.write(self.style.WARNING(msg))

    def create_user(self):
        """Create User dev and admin to local or dev mode"""

        if ENABLE_SSO is False:
            try:
                user, created = User.objects.get_or_create(
                    username='dev_admin', first_name='admin', last_name='dev', is_staff=True)
                user.set_password(PASSWD_DEV)
                project_manager_list, created, group_manager = CreatePermissions().create_group_all_groups()
                user.groups.add(group_manager)
                user.save()

                user, created = User.objects.get_or_create(
                    username='dev_user', first_name='user', last_name='dev', is_staff=False)
                user.set_password(PASSWD_DEV)
                user.save()
            except Exception as e:
                self.print(e)

    def handle(self, *args, **options):
        self.create_user()
