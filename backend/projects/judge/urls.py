from django.urls import path
from .views import JudgeApi

urlpatterns = [

    path('', JudgeApi.as_view(), name="judge-list-Create"),

]