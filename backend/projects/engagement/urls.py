from django.urls import path
from .views import EngagementApi

urlpatterns = [

    path('', EngagementApi.as_view(), name="engagement-list-create"),

]