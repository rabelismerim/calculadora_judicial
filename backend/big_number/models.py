"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""
from django.db import models

from core.abstract.models import AbstractModel
from utils import _

from rest_framework import fields

FIELD_TYPE_CHOICES = tuple((name.lower(), name) for name in sorted(
    set(name for name, obj in vars(fields).items() if isinstance(obj, type) and issubclass(obj, fields.Field))))


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


class BigNumber(AbstractModel):
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


class BigNumberMethod(AbstractModel):
    """
    A model that represents a method associated with a big number.
    Attributes:
        big_number (models.ForeignKey): A foreign key to a `BigNumber` object.
        method (models.CharField): The name of the method as a string.
        name (models.CharField): The name of the method for display purposes.
        field_type (models.CharField): The type of model field as a string.
    """
    big_number = models.ForeignKey(BigNumber, on_delete=models.PROTECT)
    method = models.CharField(_('Method in model'), max_length=50)
    name = models.CharField(_('Name for exhibition'), max_length=50)
    field_type = models.CharField(max_length=50, choices=FIELD_TYPE_CHOICES, default='charfield')

    def __str__(self):
        return f"{self.name} || {self.big_number.content_object.app_label} || {self.big_number.content_object.name}"

    def get_fields(self):
        return self.bignumbermethodfields_set.all()


class BigNumberMethodFields(AbstractModel):
    """
    A model that represents a method associated with a big number method.
    Attributes:
        big_number_method (models.ForeignKey): A foreign key to a `BigNumber` object.
        field (models.CharField): The name of the method for display purposes.
        field_type (models.CharField): The type of model field as a string.
    """
    big_number_method = models.ForeignKey(BigNumberMethod, on_delete=models.PROTECT)
    field = models.CharField(_('Field for exhibition'), max_length=50)
    field_type = models.CharField(max_length=50, choices=FIELD_TYPE_CHOICES, default='charfield')

    def __str__(self):
        return f"{self.field} || {self.big_number_method}"
