from django.urls import path

from rates.views import RateApi, RateFileApi

urlpatterns = [

    path('', RateApi.as_view(), name="rate-list-create"),
    path('file', RateFileApi.as_view(), name="ratefile-list-create"),

]
