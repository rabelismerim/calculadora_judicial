# """
# Registers the UpdateUser models with the Django admin site.
#
# This file facilitates the registration of the UpdateUser models with the Django admin site.
# By importing the admin module from the django.contrib package and the relevant models from the core.abstract.models module,
# this code registers the models with the admin site for easy management.
#
# Usage:
# - Import this file in the Django project's admin.py file to register the models with the admin site.
#
# Example:
# # In admin.py
# from django.contrib import admin
#
# admin.site.register(UpdateUser)
# """
# from django.apps import apps
# from django.contrib import admin
# from django.contrib.admin.sites import NotRegistered
#
# from core.abstract.models import UpdateUser, AbstractModel
#
# admin.site.register(UpdateUser)
#
#
# class AbstractModelAdmin(admin.ModelAdmin):
#     list_display = ('id', 'created_at', 'updated_at',)
#
#
# for model in apps.get_models():
#     if issubclass(model, AbstractModel) and not admin.site.is_registered(model):
#
#         try:
#             admin.site.unregister(model)
#         except NotRegistered:
#             pass
#         # except Exception as e:
#         #     print(e, 'err')
#         print(model, 'registeres')
#         admin.site.register(model, AbstractModelAdmin)
#
