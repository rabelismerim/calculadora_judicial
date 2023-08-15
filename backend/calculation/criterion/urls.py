from django.urls import path

from calculation.criterion.views import CriterionApi


urlpatterns = [
    path('<uuid:calculation_id>/', CriterionApi.as_view(), name="criterion-list-create"),
]
