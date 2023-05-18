"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from irrf import views
    2. Add a URL to urlpatterns:  path('', views.IrrfApi, name='irrf')
Class-based views
    1. Add an import:  from irrf import Irrf
    2. Add a URL to urlpatterns:  path('', IrrfApi.as_view(), name='irrf')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('irrf/', include('irrf.another_app.urls'))
"""
from django.urls import path

from calculation.funds.irrf.views import FundIRRFApi, FundIRRFDetailApi, StatementIRRFDetailApi, StatementIRRFApi

urlpatterns = [
    path('', FundIRRFApi.as_view(), name="funds-irrf-list-create"),
    path('<uuid:id>/', FundIRRFDetailApi.as_view(), name="document-detail"),
    path('funds/', StatementIRRFApi.as_view(), name="statement-funds-irrf-detail"),
    path('funds/<uuid:id>/', StatementIRRFDetailApi.as_view(), name="statement-fund-irrf-detail"),
]
