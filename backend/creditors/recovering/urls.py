from django.urls import path
from .views import RecoveringCreate, addRecovering

urlpatterns = [

    path('creditors/recovering/<int:recovering_pk>/', RecoveringCreate.as_view(), name="recovering-create"),
    path('creditors/recovering/', addRecovering.as_view(), name="recovering-add"),

]