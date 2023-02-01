from django.urls import path
from .views import NoticeApi


urlpatterns = [
    path('', NoticeApi.as_view(), name="notice-list-create"),
]