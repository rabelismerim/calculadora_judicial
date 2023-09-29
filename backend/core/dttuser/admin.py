"""
Registers the custom User model and Permission model to the Django admin site and defines a custom admin interface for the User model using the built-in UserAdmin class.

Modules:
- django.contrib.admin: Django's built-in administration interface.
- django.contrib.auth.admin: Built-in admin interface for the User model.
- django.utils.translation: Tools for internationalization and localization.
- .models: Custom User model.
- .forms: Custom UserCreationForm.
- django.contrib.auth.models: Built-in Permission model.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Subgroup
from .forms import UserCreationForm
from django.contrib.auth.models import Permission


class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    fieldsets = (
        (None, {'fields': ('username',)}),
        (_('Personal info'),
         {'fields': ('first_name', 'last_name', 'email', 'role', 'status', 'userpicture', 'user_img')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'groups', 'subgroups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'login_date')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'login_date'),
        }),
    )
    list_filter = ('is_staff', 'is_active', 'groups', 'subgroups')

    actions = ['reprocess_photos']

    def reprocess_photos(self, request, queryset):
        for item in queryset:
            item.create_photo(force=True)

        self.message_user(request, _('Fotos atualizadas'))

    reprocess_photos.short_description = _('Reprocessar foto dos users selecionados')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subgroup)
admin.site.register(Permission)
