from django.urls import include, path

from creditors.views import CreditorDetailApi

urlpatterns = [
    path('', CreditorDetailApi.as_view(), name="creditor-list-create"),
    path('budgets', include("creditors.budgets.urls")),
    path('classes', include("creditors.classes.urls")),
    path('notice', include("creditors.notice.urls")),
]
