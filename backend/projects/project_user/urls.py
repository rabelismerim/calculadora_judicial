from django.urls import path
from .views import ProjectUserApi

urlpatterns = [

    path('', ProjectUserApi.as_view(), name="project-user-list-create"),

]
