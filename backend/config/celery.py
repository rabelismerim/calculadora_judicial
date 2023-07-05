import os

import redis

from config.settings import celery_url

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from celery import Celery
from config import settings

app = Celery('config')

app.config_from_object('config.settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.update(CELERY_REDIS_MAX_CONNECTIONS=15)

redis_conn = redis.from_url(celery_url)
