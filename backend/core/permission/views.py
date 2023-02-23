from rest_framework import permissions
from django.apps import apps as default_apps
from django.conf import settings
from django.contrib.auth.models import Permission, Group


class CheckHasPermission(permissions.BasePermission):
    def has_permission(self, request, view):

        option = {
            'GET': 'view',
            'PUT': 'change',
            'POST': 'add',
            'DELETE': 'delete',
        }

        return request.user.has_permission(f'{option.get(request.method)}_{view.model.__name__.lower()}')


class CreatePermissions:

    def create_project_manager(self) -> tuple:
        project_manager_list = []
        create_group = {'name': 'Project Manager'}
        group_manager, created = Group.objects.get_or_create(
            defaults=create_group, **create_group)

        apps = []
        for app in settings.INSTALLED_APPS:  # Get models
            app_name = app.split('.')
            if len(app_name) > 1:  # Apps private
                app_lbl = app_name[0]
                model_name = app_name[1]
                app_models = default_apps.all_models[model_name]
                if app_models:
                    apps.append((app_lbl, app_models))

        for label, app in apps:  # Get permissions in apps
            for model in app.values():
                permissions_app = Permission.objects.filter(
                    content_type__app_label=model._meta.app_label, content_type__model=model._meta.model_name)
                if label == 'projects':  # List permissions to Project Manager group
                    project_manager_list.extend(permissions_app)

        return project_manager_list, created, group_manager
