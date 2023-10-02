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
from django.utils.html import escape
from django.utils.safestring import mark_safe
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
    list_display = ('show_image', 'id', 'username', 'first_name', 'last_name', 'email', 'is_staff')
    readonly_fields = ('show_image',)

    def show_image(self, obj):
        default_image_url = '/static/src/vue/dist/icon-app.svg'

        onerror_script = (
            "if (!this.getAttribute('data-default-tried')) {"
            "    this.setAttribute('data-default-tried', 'true');"
            f"    this.src = '/juca{default_image_url}';"
            "}"
        )
        if obj.image_url:
            return mark_safe(
                f'<img src="/juca{obj.image_url}" width="25" height="25" onerror="{onerror_script}" />')

        return mark_safe(f'<img src="/juca{default_image_url}" width="25" height="25" />')

    show_image.allow_tags = True
    show_image.short_description = _('Image')

    def reprocess_photos(self, request, queryset):
        for item in queryset:
            item.create_photo(force=True)

        self.message_user(request, _('Fotos atualizadas'))

    reprocess_photos.short_description = _('Reprocessar foto dos users selecionados')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subgroup)
admin.site.register(Permission)
