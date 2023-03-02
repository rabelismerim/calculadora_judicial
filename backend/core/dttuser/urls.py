from django.urls import path
from core.dttuser.views import UserDttApi, UserDttDetailApi


urlpatterns = [
    path('users/', UserDttApi.as_view()),
    path('user/detail/', UserDttDetailApi.as_view()),
]
