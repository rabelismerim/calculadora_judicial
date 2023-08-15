from django.urls import path
from .views import NoticeApi, NoticeUpdateApi, NoticeRecoveringApi, NoticeRecoveringUpdateApi

urlpatterns = [
    path('aj/', NoticeApi.as_view(), name="notice-list-create"),
    path('aj/<uuid:id>/', NoticeUpdateApi.as_view(), name="notice-update"),
    path('recovering/', NoticeRecoveringApi.as_view(), name="notice-recovering-list-create"),
    path('recovering/<uuid:id>/', NoticeRecoveringUpdateApi.as_view(), name="notice-recovering-update"),
]
