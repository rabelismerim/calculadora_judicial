from django.urls import path
from .views import NoticeCreate, addNotice

urlpatterns = [

    path('notice/<int:notice_pk>/', NoticeCreate.as_view(), name="notice-create"),
    path('creditors/notice/', addNotice.as_view(), name="notice-add"),

]