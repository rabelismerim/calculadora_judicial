from django.apps import AppConfig
from django.contrib import admin
from django.apps import apps
from django.db import models
from utils import _


class AbstractConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.abstract'
    verbose_name = _("Abstract User")

    def ready(self):
        """Registration for all apps that inherit the AbstractModel class to display its default fields. Adds a list
        of search fields.
        """
        from core.abstract.models import AbstractModel
        for model in apps.get_models():
            if issubclass(model, AbstractModel):
                if admin.site.is_registered(model):
                    admin_get = admin.site._registry[model]
                    if str(admin_get).endswith('.ModelAdmin'):
                        admin.site.unregister(model)

                        class AbstractModelAdmin(admin.ModelAdmin):
                            list_display = ('__str__', 'id', 'created_at', 'updated_at',)
                            readonly_fields = ('created_at', 'updated_at', 'id', 'create_user', 'update_user')
                            search_fields = get_fields(model)

                        admin.site.register(model, AbstractModelAdmin)
                    else:
                        admin_get.list_display = list(set(['__str__', 'id', 'created_at', 'updated_at'] + list(
                            admin_get.list_display)))
                        admin_get.readonly_fields = list(set(['created_at', 'updated_at', 'id', 'create_user',
                                                     'update_user'] + list(admin_get.readonly_fields)))
                        admin_get.search_fields = get_fields(model)


def get_fields(model):
    """Get a list fields of model obj."""
    from django.contrib.contenttypes.fields import GenericForeignKey

    return [field.name for field in model._meta.get_fields() if
            not field.is_relation or not isinstance(field, (
                models.OneToOneField, models.ManyToManyField, models.ForeignKey, GenericForeignKey))]
