from django.urls import path, include

from calculation.views import CalculationApi, CalculationDetailApi, IncidentApi


urlpatterns = [
    path('', CalculationApi.as_view(), name="calculation-list-create"),
    path('incident/', IncidentApi.as_view(), name="incident-list-create"),
    path('<uuid:id>/', CalculationDetailApi.as_view(), name="calculation-detail"),
    path(f'criterion/', include("calculation.criterion.urls")),
    path(f'verdict/', include("calculation.verdict.urls")),
    path(f'funds/', include("calculation.funds.urls")),
    path(f'comparative/', include("calculation.comparative.urls")),
]
