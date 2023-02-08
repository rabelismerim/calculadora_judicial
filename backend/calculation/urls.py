from django.urls import include, path

from calculation.views import CalculationApi


urlpatterns = [
    path('', CalculationApi.as_view(), name="calculation-list-Create"),
]
