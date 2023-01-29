from django.urls import path
from .views import ProjectApi

urlpatterns = [

    path('', ProjectApi.as_view(), name="project-list-Create"),

]