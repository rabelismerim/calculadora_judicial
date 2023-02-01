from django.urls import path
from .views import ArchiveRecoveringCreate, addArchiveRecovering

urlpatterns = [

    path('archive_recovering/<int:archive_recovering_pk>/', ArchiveRecoveringCreate.as_view(), name="archive_recovering-create"),
    path('creditors/archive_recovering/', addArchiveRecovering.as_view(), name="archive_recovering-add"),

]