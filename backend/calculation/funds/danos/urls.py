"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from document import views
    2. Add a URL to urlpatterns:  path('', views.DocumentApi, name='document')
Class-based views
    1. Add an import:  from document import Document
    2. Add a URL to urlpatterns:  path('', DocumentApi.as_view(), name='document')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('document/', include('document.another_app.urls'))
"""
from django.urls import path

from calculation.funds.danos.views import FundDanosDetailApi, FundDanosApi, StatementFundsDanosListApi

urlpatterns = [
    path('', FundDanosApi.as_view(), name="danos-list-create"),
    path('detail/', FundDanosApi.as_view(), name="dano-detail-create"),
    path('detail/<uuid:fund_id>/', StatementFundsDanosListApi.as_view(), name="dano-statement-detail"),
    path('<uuid:id>/', FundDanosDetailApi.as_view(), name="dano-detail"),
]
