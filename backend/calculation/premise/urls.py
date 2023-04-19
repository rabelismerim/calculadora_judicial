"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from premise import views
    2. Add a URL to urlpatterns:  path('', views.PremiseApi, name='premise')
Class-based views
    1. Add an import:  from premise import Premise
    2. Add a URL to urlpatterns:  path('', PremiseApi.as_view(), name='premise')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('premise/', include('premise.another_app.urls'))
"""
from django.urls import path
from .views import PremiseApi


urlpatterns = [
    path('', PremiseApi.as_view(), name="premise-list-create"),
]
