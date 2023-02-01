from django.urls import path
from .views import ClassesSerializer

urlpatterns = [

    path('classes/<int:classes_pk>/', ClassesSerializer.create, name="classes-create")

]