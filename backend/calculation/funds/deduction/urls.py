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

from calculation.funds.deduction.views import FundDeductionDetailApi, FundDeductionApi, StatementFundsDeductionDetailApi

urlpatterns = [
    path('', FundDeductionApi.as_view(), name="deductions-list-create"),
    path('detail/', FundDeductionApi.as_view(), name="deduction-detail-create"),
    path('detail/<uuid:id>/', StatementFundsDeductionDetailApi.as_view(), name="deduction-statement-detail"),
    path('<uuid:id>/', FundDeductionDetailApi.as_view(), name="deduction-detail"),
]
