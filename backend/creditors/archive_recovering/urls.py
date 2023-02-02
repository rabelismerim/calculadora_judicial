from django.urls import path
from .views import ArchiveRecoveringApi

urlpatterns = [
    path('', ArchiveRecoveringApi.as_view(), name="rchive_recovering-list-Create"),
]