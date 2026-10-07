from django.urls import path
from core.users.views import UserSendMailApi, UserAuthorizeApi, UserApi, UserDetailApi, GroupApi, \
    SubgroupApi, EmailListApi

urlpatterns = [
    path('users/', UserApi.as_view()),
    path('user/detail/', UserDetailApi.as_view()),
    path('groups/', GroupApi.as_view()),
    path('subgroups/', SubgroupApi.as_view()),
    path('user/authorize/', UserAuthorizeApi.as_view()),
    path('user/sendmail/', UserSendMailApi.as_view()),
    path('emails/', EmailListApi.as_view()),
]
