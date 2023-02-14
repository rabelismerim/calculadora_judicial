from django.urls import path

from calculation.verdict.views import VerdictApi



urlpatterns = [
    path('', VerdictApi.as_view(), name="verdictApi-list-create"),
]
