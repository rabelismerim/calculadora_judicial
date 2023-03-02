from django.db import models
from utils import get_user_model
from django.contrib.auth.models import Group, Permission, _user_get_permissions, _user_has_perm, _user_has_module_perms
from django.utils.translation import gettext_lazy as _
User = get_user_model()


class ProjectUser(models.Model):
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
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
    )

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
        sensitive_permissions = ['projetos',
                                 'credores']  # Only managers have permissions
        is_sensitive = perm.split('.')[0] in sensitive_permissions

        # Active superusers have all permissions, except in sensitive permissions.
        if self.is_active and self.is_superuser:
            if is_sensitive:
                # TODO: verificar nome do grupo de gerente
                return self.groups.filter(name='gerente').exists()
            return True

        # Otherwise we need to check the backends.
        return _user_has_perm(self, perm, obj)

    def has_permission(self, perm, obj=None):
        """
        Return True if the user has the specified permission in individual or group. Query all
        available auth backends, but return immediately if any backend returns
        True. Thus, a user who has permission from a single auth backend is
        assumed to have permission in general. If an object is provided, check
        permissions for that object.
        """
        sensitive_permissions = ['projetos',
                                 'credores']  # Only managers have permissions
        is_sensitive = perm.split('.')[0] in sensitive_permissions

        # Active superusers have all permissions, except in sensitive permissions.
        if hasattr(self, 'is_active') and self.is_active and self.is_superuser:
            if is_sensitive:
                # TODO: verificar nome do grupo de gerente
                return self.groups.filter(name='gerente').exists()
            return True

        return any([self.groups.filter(permissions__codename=perm).exists(), self.user_permissions.filter(codename=perm).exists()])

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

    user = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return self.user.get_full_name
