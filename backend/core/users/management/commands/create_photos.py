from django.core.management.base import BaseCommand

from utils import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'run create user dev and admin'

    def create_photo(self):
        """Create User dev and admin to local or dev mode"""

        users = User.objects.all()
        for item in users:
            item.create_photo(force=True)

    def handle(self, *args, **options):
        self.create_photo()
