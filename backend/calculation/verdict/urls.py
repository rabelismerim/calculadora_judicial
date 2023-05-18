from django.urls import path

from calculation.verdict.views import VerdictApi, VerdictDetailApi

urlpatterns = [
    path('', VerdictApi.as_view(), name="verdictApi-create"),
    path('<uuid:calculation_id>/', VerdictDetailApi.as_view(), name="verdictApi-list"),
]
