"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from statement_pj import views
    2. Add a URL to urlpatterns:  path('', views.StatementPJApi, name='statement_pj')
Class-based views
    1. Add an import:  from statement_pj import Statement_Pj
    2. Add a URL to urlpatterns:  path('', StatementPJApi.as_view(), name='statement_pj')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('statement_pj/', include('statement_pj.another_app.urls'))
"""
from django.urls import path
from .views import StatementPJApi

urlpatterns = [
    path('<uuid:calculation_id>', StatementPJApi.as_view(), name="statement_pj-list-create"),
]
