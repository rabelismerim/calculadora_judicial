from django.urls import path
from .views import ArchiveCreate, addArchive

urlpatterns = [

    path('archive/<int:archive_pk>/', ArchiveCreate.as_view(), name="archive-create"),
    path('creditors/archive/', addArchive.as_view(), name="archive-add"),

]