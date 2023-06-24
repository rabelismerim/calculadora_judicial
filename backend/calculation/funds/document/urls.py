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

from calculation.funds.document.views import FundDocumentDetailApi, FundDocumentApi, StatementFundsIRRFListApi

urlpatterns = [
    path('', FundDocumentApi.as_view(), name="documents-list-create"),
    path('detail/', FundDocumentApi.as_view(), name="document-detail-create"),
    path('detail/<uuid:fund_id>/', StatementFundsIRRFListApi.as_view(), name="document-statement-detail"),
    path('<uuid:id>/', FundDocumentDetailApi.as_view(), name="document-detail"),
]
