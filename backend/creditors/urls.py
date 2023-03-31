from django.urls import include, path

from creditors.views import CreditorDetailApi, CreditorCreateApi, CreditorApi, CreditorUpdateApi

urlpatterns = [
    path('', CreditorApi.as_view(), name="creditor-list-create"),
    path('detail/<uuid:id>/', CreditorDetailApi.as_view(), name="creditor-detail"),
    path('<uuid:id>/', CreditorUpdateApi.as_view(), name="creditor-update"),
    path('options/', CreditorCreateApi.as_view(), name="creditor-options"),
    # path('classes', include("creditors.classes.urls")),
    path('notice/', include("creditors.notice.urls")),
]
