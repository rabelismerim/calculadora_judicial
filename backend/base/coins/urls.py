from django.urls import path
from .views import CoinsApi


urlpatterns = [
    path('', CoinsApi.as_view(), name="coins-list-create"),
]
