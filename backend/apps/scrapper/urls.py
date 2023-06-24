"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from scrapper import views
    2. Add a URL to urlpatterns:  path('', views.ScrapperApi, name='scrapper')
Class-based views
    1. Add an import:  from scrapper import Scrapper
    2. Add a URL to urlpatterns:  path('', ScrapperApi.as_view(), name='scrapper')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('scrapper/', include('scrapper.another_app.urls'))
"""
from django.urls import path
from .views import ScrapperApi


urlpatterns = [
    path('', ScrapperApi.as_view(), name="scrapper-list-create"),
]
