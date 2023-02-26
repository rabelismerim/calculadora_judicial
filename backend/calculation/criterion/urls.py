from django.urls import path

from calculation.criterion.views import CriterionApi


urlpatterns = [
    path('', CriterionApi.as_view(), name="criterion-list-create"),
]
