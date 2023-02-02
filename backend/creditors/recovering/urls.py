from django.urls import path
from .views import RecoveringApi


urlpatterns = [
    path('', RecoveringApi.as_view(), name="recovering-list-Create"),
]