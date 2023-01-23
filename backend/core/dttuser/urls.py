from django.urls import path
from core.dttuser.views import UserDttApi


urlpatterns = [
    path('users', UserDttApi.as_view()),
]