"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from comparative import views
    2. Add a URL to urlpatterns:  path('', views.ComparativeApi, name='comparative')
Class-based views
    1. Add an import:  from comparative import Comparative
    2. Add a URL to urlpatterns:  path('', ComparativeApi.as_view(), name='comparative')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('comparative/', include('comparative.another_app.urls'))
"""
from django.urls import path
from .views import ComparativeApi, ComparativeDetailApi


urlpatterns = [
    path('', ComparativeApi.as_view(), name="comparative-list"),
    path('<uuid:calculation_id>/', ComparativeDetailApi.as_view(),
         name="comparative-detail-create"),
]
