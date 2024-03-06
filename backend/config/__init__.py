import os

django_module = os.environ.get('DJANGO_SETTINGS_MODULE')

if not django_module:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    import django

    django.setup()

from celery import shared_task
from config.celery import app as celery_app

__all__ = ("celery_app",)


@shared_task()  # 1
def start_celery():
    print('||Started Celery||\n')
    return True
