from django.db import models
from base.models import AbstractDescription


class Archive(AbstractDescription):
    archive_json = models.TextField(blank=True)
