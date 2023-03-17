"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from funds import views
    2. Add a URL to urlpatterns:  path('', views.FundsApi, name='funds')
Class-based views
    1. Add an import:  from funds import Funds
    2. Add a URL to urlpatterns:  path('', FundsApi.as_view(), name='funds')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('funds/', include('funds.another_app.urls'))
"""
from django.urls import path
from .views import FundsApi, StatementFundsApi, StatementFundsDetailApi

urlpatterns = [
    path('', FundsApi.as_view(), name="funds-list-create"),
    path('statement/funds/', StatementFundsApi.as_view(), name="statement-funds-list-create"),
    path('statement/funds/<uuid:id>/', StatementFundsDetailApi.as_view(), name="statement-funds-list-create"),
#     path('statement/calculation/funds/<uuid:calculation_id>/', StatementFundsCalculationApi.as_view(),
#          name="calculation-statement-funds-list"),
]
