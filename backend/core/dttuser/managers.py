from django.contrib.auth.models import UserManager


class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        raise ValueError('Superuser creation is disabled.')

    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        raise ValueError('Bulk creation is disabled.')

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValueError('Bulk update is disabled.')

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields["is_staff"] = False
        extra_fields["is_active"] = False
        return self._create_user(username, email, password, **extra_fields)
