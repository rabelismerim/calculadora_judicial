"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from statement import views
    2. Add a URL to urlpatterns:  path('', views.StatementApi, name='statement')
Class-based views
    1. Add an import:  from statement import Statement
    2. Add a URL to urlpatterns:  path('', StatementApi.as_view(), name='statement')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('statement/', include('statement.another_app.urls'))
"""
from django.urls import path
from .views import StatementApi

urlpatterns = [
    path('<uuid:calculation_id>/', StatementApi.as_view(), name="statement-list"),
]
