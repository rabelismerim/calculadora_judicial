from django.urls import path
from .views import ArchiveApi

urlpatterns = [
    path('', ArchiveApi.as_view(), name="archive-list-Create"),
]