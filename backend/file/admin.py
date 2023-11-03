"""
Registers the File models with the Django admin site.

This file facilitates the registration of the File models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the file.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(File)
"""
from django.contrib import admin, messages
from utils import _

from file.models import File, GenericModelPath, ErrorFile

admin.site.register(GenericModelPath)
admin.site.register(ErrorFile)


def reprocess_task(modeladmin, request, queryset):
    """
    Reprocesses the selected tasks.

    Args:
        modeladmin: The ModelAdmin instance.
        request: The current request.
        queryset: A QuerySet containing the selected tasks.

    Returns:
        None
    """
    for obj in queryset:
        model = obj.generic_path.content_object.model_class().objects.filter(id=obj.object_id).first()
        success, msg = model.parse_file(obj, raise_exception=False)
        if success:
            messages.success(request, msg)
        else:
            messages.warning(request, msg)


reprocess_task.short_description = _("Reprocess tasks")


class FileModelAdmin(admin.ModelAdmin):
    """
   Admin configuration for the FileModel model.

   Attributes:
       list_display (tuple): A tuple of field names to display in the admin list view.
       actions (list): A list of actions that can be performed on the selected objects.

   Methods:
       reprocess_task: Action method to reprocess the selected tasks.
   """
    list_display = ('id', 'task_result', 'content_type')
    actions = [reprocess_task]


admin.site.register(File, FileModelAdmin)
