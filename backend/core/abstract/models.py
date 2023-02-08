import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from crum import get_current_request
from django.db.models.signals import pre_save
from django.forms import model_to_dict
from utils import get_user_model

User = get_user_model()


class AbstractModel(models.Model):
    """Abstraction of common fields in all models"""
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(
        'Data de criação', auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    create_user = models.UUIDField()
    update_user = models.UUIDField(null=True)

    class Meta:
        abstract = True
        ordering = ('created_at',)

    def __init__(self, *args, **kwargs):
        super(AbstractModel, self).__init__(*args, **kwargs)
        self.__initial = self._dict

    @staticmethod
    def __get_user(id_):
        """Abstract get User by UUID"""
        try:
            user = User.objects.filter(id=id_).first()
            if user:
                return user.get_full_name
        except:
            pass
        return 'Não encontrado'

    @property
    def get_update_user(self):
        """Get update User by UUID"""
        if self.update_user:
            return self.__get_user(self.update_user)
        return 'Não encontrado'

    @property
    def get_create_user(self):
        """Get create User by UUID"""
        if self.create_user:
            return self.__get_user(self.create_user)
        return 'Não encontrado'

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

    @property
    def updates(self):
        return list(UpdateUser.objects.filter(object_id=self.id).order_by('-created_at'))


class UpdateUser(models.Model):
    """Model template to catch all updates made to the model"""
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    object_id = models.UUIDField()  # uuid AbstractModel
    field_changed = models.CharField(
        'Field alterado', max_length=100, null=True)
    current_value = models.CharField('Valor atual', max_length=400, null=True)
    previous_value = models.CharField(
        'Valor anterior', max_length=400, null=True)
    create_user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    content_object = GenericForeignKey()

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f'Field alterado: {self.field_changed} | Valor anterior: {self.previous_value} | Valor atual: {self.current_value} | User: {self.create_user} | Hora de criação: {self.created_at}'


def get_user(sender, **kwargs):
    """Get User on request"""
    instance = kwargs.get('instance')
    requests_ = get_current_request()
    user_id = requests_.user.id if requests_ else None
    instance.create_user_id = user_id
    if hasattr(instance, 'changed_fields') and hasattr(instance, 'id'):
        for field, values in instance.changed_fields:
            UpdateUser.objects.create(field_changed=field, previous_value=values[0], current_value=values[1],
                                      create_user_id=user_id, object_id=instance.id,
                                      content_object=instance)

    if hasattr(instance, 'create_user'):
        if instance.create_user is None:
            instance.create_user = user_id
        else:
            instance.update_user = user_id


pre_save.connect(get_user, dispatch_uid=AbstractModel)
