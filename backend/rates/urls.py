from django.urls import path

from rates.views import RateApi

urlpatterns = [

    path('', RateApi.as_view(), name="rate-list-create"),

]
