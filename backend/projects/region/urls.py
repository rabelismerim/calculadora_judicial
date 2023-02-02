from django.urls import path
from .views import RegionApi

urlpatterns = [

    path('', RegionApi.as_view(), name="region-list-Create"),

]