from django.urls import path, include

from calculation.views import CalculationApi


urlpatterns = [
    path('', CalculationApi.as_view(), name="calculation-list-create"),
    path(f'criterion/', include("calculation.criterion.urls")),
    path(f'verdict/', include("calculation.verdict.urls")),
]
