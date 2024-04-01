from django.urls import path
from .views import NoticeApi, NoticeUpdateApi, NoticeRecoveringApi, NoticeRecoveringUpdateApi, NoticeDetailApi, \
    NoticeRecoveringDetailApi

urlpatterns = [
    # TODO Marcelo: Criar um get que traga os notices AJ e RJ recebendo o id do credor
    path('aj/', NoticeApi.as_view(), name="notice-list-create"),
    path('aj/<uuid:id>/', NoticeUpdateApi.as_view(), name="notice-update"),
    path('aj/creditor/<uuid:creditor_id>/', NoticeDetailApi.as_view(), name="notice-detail"),
    path('recovering/', NoticeRecoveringApi.as_view(), name="notice-recovering-list-create"),
    path('recovering/<uuid:id>/', NoticeRecoveringUpdateApi.as_view(), name="notice-recovering-update"),
    path('recovering/creditor/<uuid:creditor_id>/', NoticeRecoveringDetailApi.as_view(), name="notice-recovering-detail"),
]
