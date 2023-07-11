"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from file import views
    2. Add a URL to urlpatterns:  path('', views.FileApi, name='file')
Class-based views
    1. Add an import:  from file import File
    2. Add a URL to urlpatterns:  path('', FileApi.as_view(), name='file')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('file/', include('file.another_app.urls'))
"""
from django.urls import path
from .views import FileApi, FileDetailApi, FileExamplesApi, FileExampleDetailApi, FilePathsApi, FileErrorDetailApi, \
    PathFileListApi

urlpatterns = [
    path('create/<str:path>/', FileApi.as_view(), name="file-create"),
    path('detail/<uuid:id>/', FileDetailApi.as_view(), name="file-detail"),
    path('detail/<str:path>/<uuid:object_id>/', PathFileListApi.as_view(), name="file-detail"),
    path('error/detail/<uuid:id>/', FileErrorDetailApi.as_view(), name="file-detail"),
    path('example/', FilePathsApi.as_view(), name="files-list"),
    path('example/<str:path>/', FileExamplesApi.as_view(), name="file-path-detail"),
    path('example/<str:path>/<str:name>/', FileExampleDetailApi.as_view(), name="file-name-detail"),
]
