from django.urls import path, include

from calculation.views import CalculationApi, CalculationDetailApi, IncidentApi, ChangeStepApi, CalculationListApi

urlpatterns = [
    path('', CalculationApi.as_view(), name="calculation-create"),
    path('creditor/<uuid:creditor_id>/', CalculationListApi.as_view(), name="calculation-list-creditor"),
    path('<uuid:id>/change_step/', ChangeStepApi.as_view(), name="calculation-change-step"),
    path('incident/', IncidentApi.as_view(), name="incident-list-create"),
    path('<uuid:id>/', CalculationDetailApi.as_view(), name="calculation-detail"),
    path(f'criterion/', include("calculation.criterion.urls")),
    path(f'verdict/', include("calculation.verdict.urls")),
    path(f'funds/', include("calculation.funds.urls")),
    path(f'comparative/', include("calculation.comparative.urls")),
    path(f'statement/', include("calculation.statement.urls")),
]
