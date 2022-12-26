from django.contrib.auth.models import UserManager


class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        raise ValueError('Superuser creation is disabled.')
    
    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        raise ValueError('Bulk creation is disabled.')
    
    def bulk_update(self, objs, fields, batch_size=None):
        raise ValueError('Bulk update is disabled.')