"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from statement_pf import views
    2. Add a URL to urlpatterns:  path('', views.StatementPFApi, name='statement_pf')
Class-based views
    1. Add an import:  from statement_pf import Statement_Pf
    2. Add a URL to urlpatterns:  path('', StatementPFApi.as_view(), name='statement_pf')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('statement_pf/', include('statement_pf.another_app.urls'))
"""
from django.urls import path
from .views import StatementPFApi


urlpatterns = [
    path('', StatementPFApi.as_view(), name="statement_pf-list-create"),
]
