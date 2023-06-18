"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from big_number import views
    2. Add a URL to urlpatterns:  path('', views.BigNumberApi, name='big_number')
Class-based views
    1. Add an import:  from big_number import BigNumber
    2. Add a URL to urlpatterns:  path('', BigNumberApi.as_view(), name='big_number')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('big_number/', include('big_number.another_app.urls'))
"""
from django.urls import path
from .views import BigNumberApi


urlpatterns = [
    path('<str:path>/<uuid:id>/', BigNumberApi.as_view(), name="big_number-list-create"),
    path('<str:path>/', BigNumberApi.as_view(), name="big_number-list-create"),
]
