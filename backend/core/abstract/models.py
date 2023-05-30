import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from crum import get_current_request
from django.db.models import Q
from django.db.models.signals import pre_save, pre_delete
from django.forms import model_to_dict
from utils import get_user_model, _

User = get_user_model()


class AbstractModel(models.Model):
    """Abstraction of common fields in all models"""
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(_('Creation date'), auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    create_user = models.CharField(_('Creation username'), max_length=150, null=True)
    update_user = models.CharField(_('Update username'), max_length=150, null=True)
    objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ('-created_at', '-updated_at')

    def __init__(self, *args, **kwargs):
        super(AbstractModel, self).__init__(*args, **kwargs)
        self.__initial = self._dict

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.items()

    def get_field_diff(self, field_name):
        """Returns a diff for field if it's changed and None otherwise."""
        return self.diff.get(field_name, None)

    def save(self, *args, **kwargs):
        """Saves model and set initial state."""
        super(AbstractModel, self).save(*args, **kwargs)
        self.__initial = self._dict

    @property
    def _dict(self):
        """Model to dictionary"""
        return model_to_dict(self, fields=[field.name for field in self._meta.fields])

    def dict_update(self, *args, **kwargs):
        """Update fields through a dictionary"""
        for name, values in kwargs.items():
            try:
                attr_value = getattr(self, name)
                if attr_value != values:
                    setattr(self, name, values)
            except KeyError:
                pass
        self.save()
        return self

    def get_historical(self):
        return list(UpdateUser.objects.filter(object_id=self.id).exclude(
            Q(field_changed='update_user') | Q(current_value__regex=r'^[\w-]{36}$')).order_by('-created_at'))


class UpdateUser(models.Model):
    """Model template to catch all updates made to the model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    field_changed = models.CharField(_('Field changed'), max_length=100, null=True)
    field_changed_display = models.CharField(_('Field changed display'), max_length=100, null=True)
    current_value = models.CharField(_('Current value'), max_length=400, null=True)
    previous_value = models.CharField(_('Previous value '), max_length=400, null=True)
    create_user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)

    object_id = models.UUIDField()  # uuid AbstractModel
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    content_object = GenericForeignKey()

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return str(self.field_changed)


def save_obj(sender, **kwargs):
    """Get User on request"""
    instance = kwargs.get('instance')
    requests_ = get_current_request()
    username = (requests_.user.username.strip() or None) if requests_ else 'anonymous'
    user_id = requests_.user.id if requests_ else None
    instance.create_user_id = user_id
    if hasattr(instance, 'changed_fields') and hasattr(instance, 'id'):
        for field, values in instance.changed_fields:
            previous_value = values[0]
            current_value = values[1]
            new_field = instance._meta.get_field(field)
            if hasattr(new_field, 'choices') and getattr(instance, f'get_{field}_display', None):
                choices = dict(new_field.choices)
                previous_value = choices.get(previous_value, previous_value)
                current_value = choices.get(current_value, current_value)
            UpdateUser.objects.create(field_changed=field, field_changed_display=new_field.verbose_name,
                                      previous_value=previous_value, current_value=current_value,
                                      create_user_id=user_id, object_id=instance.id, content_object=instance)

    if hasattr(instance, 'create_user'):
        if instance.create_user is None:
            # if isinstance(username, User):
                instance.create_user = username
        else:
            instance.update_user = username


pre_save.connect(save_obj, dispatch_uid=AbstractModel)


def delete_obj(sender, **kwargs):
    """Get User on request"""
    instance = kwargs.get('instance')
    requests_ = get_current_request()
    username = (requests_.user.username.strip() or None) if requests_ else 'anonymous'
    user_id = requests_.user.id if requests_ else None
    instance.create_user_id = user_id
    if hasattr(instance, 'id'):
        previous_value = instance.__str__()
        current_value = 'deleted'

        UpdateUser.objects.create(field_changed='object', field_changed_display='object',
                                  previous_value=previous_value, current_value=current_value,
                                  create_user_id=user_id, object_id=instance.id, content_object=instance)

    if hasattr(instance, 'create_user'):
        if instance.create_user is None:
            if isinstance(username, User):
                instance.create_user = username
        else:
            instance.update_user = username


pre_delete.connect(delete_obj, dispatch_uid=AbstractModel)
