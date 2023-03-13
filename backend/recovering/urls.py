from django.urls import include, path
from .views import RecoveringApi


urlpatterns = [
    path('', RecoveringApi.as_view(), name="recovering-list-create"),
    path('archive_recovering/', include("recovering.archive_recovering.urls")),
]
