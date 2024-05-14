from django.urls import include, path

from creditors.views import CreditorDetailApi, CreditorCreateApi, CreditorApi, CreditorUpdateApi, CreditorListApi, \
    CreditorCheckApi, CalcValidateApi, LegalPendenciesApi, LegalPendenciesDetailApi, CreditorInactiveListApi, \
    CreditorListLegalNumberApi

urlpatterns = [
    path('', CreditorApi.as_view(), name="creditor-create"),
    path('check/<uuid:recovering_id>/', CreditorCheckApi.as_view(), name="creditor-check"),
    path('project/<uuid:recovering__project_id>/', CreditorListApi.as_view(), name="creditor-list"),
    path('recovering_legal_number/<uuid:recovering__project_id>/<str:recovering__entity__legal_number>/',
         CreditorListLegalNumberApi.as_view(),
         name="creditor-list-legal-number"),
    path('project/inactive/<uuid:project_id>/', CreditorInactiveListApi.as_view(), name="creditor-inactive-list"),
    path('detail/<uuid:id>/', CreditorDetailApi.as_view(), name="creditor-detail"),
    path('legal_pendencies/', LegalPendenciesApi.as_view(), name="legal-pendencies-create"),
    path('legal_pendencies/<uuid:id>/', LegalPendenciesDetailApi.as_view(), name="legal-pendencies-detail"),
    path('<uuid:id>/', CreditorUpdateApi.as_view(), name="creditor-update"),
    path('<uuid:id>/validate/', CalcValidateApi.as_view(), name="calculation-validate"),

    path('options/', CreditorCreateApi.as_view(), name="creditor-options"),
    # path('classes', include("creditors.classes.urls")),
    path('notice/', include("creditors.notice.urls")),
]
