"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from integrations import views
    2. Add a URL to urlpatterns:  path('', views.IntegrationsApi, name='integrations')
Class-based views
    1. Add an import:  from integrations import Integrations
    2. Add a URL to urlpatterns:  path('', IntegrationsApi.as_view(), name='integrations')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('integrations/', include('integrations.another_app.urls'))
"""
from django.urls import path

from calculation.funds.integrations.views import StatementIntegrationsApi, StatementIntegrationsDetailApi

urlpatterns = [
    path('', StatementIntegrationsApi.as_view(),
         name="statement-funds-integrations-list-create"),
    path('<uuid:id>/', StatementIntegrationsDetailApi.as_view(),
         name="statement-funds-integrations-detail"),
]
