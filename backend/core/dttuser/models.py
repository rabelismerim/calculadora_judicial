import itertools

import base64
import hashlib
import uuid

from django.contrib.sessions.models import Session
from django.core.files.base import ContentFile

from django.contrib.auth.models import AbstractBaseUser, Group, Permission, _user_get_permissions, _user_has_perm, \
    _user_has_module_perms
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from utils import check_choice
from .managers import CustomUserManager
from config.settings import ENABLE_SSO, IS_PROD

ROLES_CHOICES = (
    ('S', _('Partner')),
    ('G', _('Manager')),
    ('D', _('Director')),
    ('A', _('Analyst')),
    ('C', _('Senior advisor')),
    ('R', _('Robo')),
)

ROLES_EMAIL = ['G', 'D', 'C']  # Roles that can receive email to approve the user

STATUS_CHOICES = (  # Status para o User DTT
    ('A', _('Active')),
    ('I', _('Inactive')),
    ('P', _('Pending')),
    ('R', _('Rejected')),
    ('F', _('Vacation')),
)
STATUS_ACTIVE = ['A', 'C']  # Definir status ativo


class SubgroupManager(models.Manager):
    """
    The manager for the auth's Subgroup model.
    """

    use_in_migrations = True

    def get_by_natural_key(self, name):
        return self.get(name=name)


class Subgroup(models.Model):
    """
    Subgroups are a generic way of categorizing users to apply permissions, or
    some other label, to those users. A user can belong to any number of
    subgroups.

    A user in a subgroup automatically has all the permissions granted to that
    subgroup. For example, if the subgroup 'Site editors' has the permission
    can_edit_home_page, any user in that subgroup will have that permission.

    Beyond permissions, subgroups are a convenient way to categorize users to
    apply some label, or extended functionality, to them. For example, you
    could create a subgroup 'Special users', and you could write code that would
    do special things to those users -- such as giving them access to a
    members-only portion of your site, or sending them members-only email
    messages.
    """

    name = models.CharField(_("name"), max_length=150, unique=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("permissions"),
        blank=True,
    )

    objects = SubgroupManager()

    def __str__(self):
        return self.name

    def natural_key(self):
        return self.name,


class PermissionsMixin(models.Model):
    """
    Add the fields and methods necessary to support the Group and Permission
    models using the ModelBackend.
    """
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        # related_name="user_set",
        related_query_name="user",
    )
    subgroups = models.ManyToManyField(
        Subgroup,
        verbose_name=_('subgroups'),
        blank=True,
        help_text=_(
            'The subgroups this user belongs to. A user will get all permissions '
            'granted to each of their subgroups.'
        ),
        # related_name="user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        # related_name="user_set",
        related_query_name="user",
    )

    class Meta:
        abstract = True
        ordering = ('-created_at', '-updated_at')

    def get_user_permissions(self, obj=None):
        """
        Return a list of permission strings that this user has directly.
        Query all available auth backends. If an object is passed in,
        return only permissions matching this object.
        """
        return _user_get_permissions(self, obj, 'user')

    def get_group_permissions(self, obj=None):
        """
        Return a list of permission strings that this user has through their
        groups. Query all available auth backends. If an object is passed in,
        return only permissions matching this object.
        """
        return _user_get_permissions(self, obj, 'group')

    def get_subgroup_permissions(self, obj=None):
        """
        Return a list of permission strings that this user has through their
        groups. Query all available auth backends. If an object is passed in,
        return only permissions matching this object.
        """
        return _user_get_permissions(self, obj, 'subgroup')

    def get_all_permissions(self, obj=None):
        return _user_get_permissions(self, obj, 'all')

    def has_perm(self, perm, obj=None):
        """
        Return True if the user has the specified permission. Query all
        available auth backends, but return immediately if any backend returns
        True. Thus, a user who has permission from a single auth backend is
        assumed to have permission in general. If an object is provided, check
        permissions for that object.
        """
        sensitive_permissions = ['view_formula']  # Only managers have permissions
        is_sensitive = perm.split('.')[0] in sensitive_permissions

        # Active superusers have all permissions, except in sensitive permissions.
        if self.is_active and self.is_superuser and perm in sensitive_permissions is False:
            if is_sensitive is False:
                return True

        # Otherwise we need to check the backends.
        return _user_has_perm(self, perm, obj)

    def has_permission(self, perms: list or str, obj=None):
        """
        Return True if the user has the specified permission in individual or group. Query all
        available auth backends, but return immediately if any backend returns
        True. Thus, a user who has permission from a single auth backend is
        assumed to have permission in general. If an object is provided, check
        permissions for that object.
        """
        if isinstance(perms, str):
            perms = [perms]
        has_perm = False

        for perm in perms:
            sensitive_permissions = ['view_formula']  # Only managers have permissions
            is_sensitive = perm.split('.')[0] in sensitive_permissions
            # Active superusers have all permissions, except in sensitive permissions.
            if self.is_active and self.is_superuser and is_sensitive is False:
                if is_sensitive is False:
                    return True

        for perm in perms:
            has_perm = any([self.groups.filter(permissions__codename=perm).exists(),
                            self.user_permissions.filter(codename=perm).exists()])
            if has_perm is False:
                break
        return has_perm

    def has_perms(self, perm_list, obj=None):
        """
        Return True if the user has each of the specified permissions. If
        object is passed, check if the user has all required perms for it.
        """
        return all(self.has_perm(perm, obj) for perm in perm_list)

    def has_module_perms(self, app_label):
        """
        Return True if the user has any permissions in the given app label.
        Use similar logic as has_perm(), above.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        return _user_has_module_perms(self, app_label)


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={'unique': _("A user with that username already exists.")},
    )
    password = models.CharField(max_length=128, editable=False)
    role = models.CharField(_('role'), default="A", max_length=1, choices=ROLES_CHOICES)
    status = models.CharField('status', default="P", max_length=1, choices=STATUS_CHOICES)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    userpicture = models.TextField(_('user picture'), blank=True)
    user_img = models.ImageField(_('User img'), upload_to='juca/profile/%Y/%m/%d/', blank=True, null=True)
    login_date = models.DateField(_('Login today'), null=True, blank=True
                                  )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        blank=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    def create_photo(self, force=False):
        if not self.userpicture:
            return
        try:
            data = ContentFile(base64.b64decode(self.userpicture))
            image_data = base64.b64decode(self.userpicture)
            file_hash = hashlib.md5(image_data).hexdigest()
            file_name = f"{file_hash}.jpeg"
            if (not self.user_img or str(self.user_img.name) in file_name is False) or force:
                self.user_img.save(file_name, data, save=True)  # image is User's model field
                self.save()
        except Exception as e:
            print(e, 'err save img in base64')

    @property
    def image_url(self):
        if self.user_img:
            return self.user_img.url

    @property
    def is_superuser(self):
        return self.is_active and self.is_staff

    @classmethod
    def from_db(cls, db, field_names, values):
        # Default implementation of from_db() (subject to change and could
        # be replaced with super()).
        if len(values) != len(cls._meta.concrete_fields):
            values = list(values)
            values.reverse()
            values = [
                values.pop() if f.attname in field_names else models.DEFERRED
                for f in cls._meta.concrete_fields
            ]
        instance = cls(*values)
        instance._state.adding = False
        instance._state.db = db
        # customization to store the original field values on the instance
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    @property
    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def get_list_permissions(self):
        """Return the list permissions for the user."""
        user_permissions = list(self.user_permissions.all().values('name', 'codename'))
        group_permissions = (group.permissions.all().values('name', 'codename') for group in self.groups.all())
        return list(itertools.chain(user_permissions, *group_permissions))

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # Allowing or blocking to use django user with password
        self.is_active = self.status in STATUS_ACTIVE
        if IS_PROD is False:
            if not self._state.adding and (self.id != self._loaded_values['id']):
                raise ValueError(_("Updating the value of id isn't allowed"))
            if ENABLE_SSO:
                self.set_unusable_password()
        else:
            if self.username == 'dev_admin':
                self.is_active = True
                self.status = 'A'
        return super().save(force_insert, force_update, using, update_fields)

    def set_status_by_choice(self, choice):
        check_choice(choice, STATUS_CHOICES)
        self.status = choice
        self.save()

    @staticmethod
    def get_status_pending():
        return 'P'

    def invalidate_user_sessions(self):
        # Filtra as sessões relacionadas ao usuário
        return
        Session.objects.filter(session_data__contains=self.id).delete()
