from django.urls import include, path

from recovering.views import RecoveringApi, RecoveringCheckApi, RecoveringLegalNumberApi, RecoveringProjectApi

urlpatterns = [
    path('', RecoveringApi.as_view(), name="recovering-list-create"),
    path('legal_number/<uuid:project_id>/<str:entity__legal_number>/', RecoveringLegalNumberApi.as_view(),
         name="recovering-list-legal-number"),
    path('project/<uuid:project_id>/', RecoveringProjectApi.as_view(),
         name="recovering-list-project"),
    path('check/<uuid:project_id>/', RecoveringCheckApi.as_view(), name="recovering-list-create"),
    path('archive_recovering/', include("recovering.archive_recovering.urls")),
]
