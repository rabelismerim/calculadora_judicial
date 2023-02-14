from django.urls import include, path

from creditors.views import CreditorDetailApi, CreditorCreateApi, CreditorApi

urlpatterns = [
    path('', CreditorApi.as_view(), name="creditor-list-create"),
    path('<uuid:id>', CreditorDetailApi.as_view(), name="creditor-detail"),
    path('options', CreditorCreateApi.as_view(), name="creditor-options"),
    path('budgets', include("creditors.budgets.urls")),
    path('classes', include("creditors.classes.urls")),
    path('notice', include("creditors.notice.urls")),
]
