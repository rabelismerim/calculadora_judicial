from django.urls import path
from .views import ClassesApi


urlpatterns = [
    path('', ClassesApi.as_view(), name="classes-list-create")
]