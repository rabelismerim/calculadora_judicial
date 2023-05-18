from django.urls import path
from core.dttuser.views import UserSendMailDttApi, UserAuthorizeDttApi, UserDttApi, UserDttDetailApi, GroupApi, SubgroupApi


urlpatterns = [
    path('users/', UserDttApi.as_view()),
    path('user/detail/', UserDttDetailApi.as_view()),
    path('groups/', GroupApi.as_view()),
    path('subgroups/', SubgroupApi.as_view()),
    path('user/authorize/', UserAuthorizeDttApi.as_view()),
    path('user/sendmail/', UserSendMailDttApi.as_view()),
]
