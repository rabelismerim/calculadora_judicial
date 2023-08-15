from django.urls import include, path
from .views import RecoveringApi, RecoveringCheckApi

urlpatterns = [
    path('', RecoveringApi.as_view(), name="recovering-list-create"),
    path('check/<uuid:project_id>/', RecoveringCheckApi.as_view(), name="recovering-list-create"),
    path('archive_recovering/', include("recovering.archive_recovering.urls")),
]
