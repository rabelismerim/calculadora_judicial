from django.urls import path
from core.dttuser.views import UserDttApi, UserDttDetailApi, GroupApi


urlpatterns = [
    path('users/', UserDttApi.as_view()),
    path('user/detail/', UserDttDetailApi.as_view()),
    path('groups/', GroupApi.as_view()),
]
