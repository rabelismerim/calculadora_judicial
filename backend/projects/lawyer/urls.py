from django.urls import path
from .views import LawyerApi

urlpatterns = [

    path('', LawyerApi.as_view(), name="lawyer-list-Create"),

]