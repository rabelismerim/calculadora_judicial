from django.urls import path
from core.dttuser.views import UserAuthorizeDttApi, UserDttApi, UserDttDetailApi, GroupApi


urlpatterns = [
    path('users/', UserDttApi.as_view()),
    path('user/detail/', UserDttDetailApi.as_view()),
    path('groups/', GroupApi.as_view()),
    path('user/authorize/', UserAuthorizeDttApi.as_view()),
]
