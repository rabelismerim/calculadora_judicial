"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""
import pandas as pd
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django_celery_results.models import TaskResult

from core.abstract.models import AbstractModel
from utils import _

ERROR_STATUS_CHOICES = (
    ('R', _('Registered')),
    ('C', _('In correction')),
    ('E', _('Resolved')),
    ('P', _('Processing error')),
)


class GenericOneToOneField(models.OneToOneField):
    """A subclass of OneToOneField that sets the related model to `contenttypes.ContentType` by default.
    """

    def __init__(self, *args, **kwargs):
        kwargs['to'] = 'contenttypes.ContentType'
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['to']
        return name, path, args, kwargs


class GenericModelPath(AbstractModel):
    """
    A model that represents a large number and its related content object.
    Attributes:
        content_object (GenericOneToOneField): A generic one-to-one field that can refer to any content type.
        path (models.CharField): The path to the big number represented as a string.
    """
    content_object = GenericOneToOneField(
        to='contenttypes.ContentType',
        on_delete=models.PROTECT,
        related_name='%(app_label)s_%(class)s_related',
    )
    path = models.CharField(_('Path'), max_length=50)

    def __str__(self):
        return f"{self.path} || {self.content_object.app_label} || {self.content_object.name}"


class File(AbstractModel):
    """
    A class representing a File.

    Attributes:
    """
    file = models.FileField(upload_to='juca/files/%Y/%m/%d/')
    generic_path = models.ForeignKey(GenericModelPath, on_delete=models.PROTECT)
    task_result = models.ForeignKey(TaskResult, on_delete=models.PROTECT, null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)

    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')


    def get_task_result(self):
        if self.task_result:
            return self.task_result.get_status_display()

    def get_excel_headers(self) -> tuple:
        # Ler o arquivo Excel usando pandas
        with self.file as file_obj:
            read = file_obj.read()
            df = pd.read_excel(read)
            headers = df.columns.tolist()

        return self.id, read, headers


class ErrorFile(AbstractModel):
    """
    A class representing a FileError.

    Attributes:
    """
    file = models.ForeignKey(File, on_delete=models.PROTECT)
    error = models.TextField(_("Error"))
    status = models.CharField(default="R", max_length=1, choices=ERROR_STATUS_CHOICES)
