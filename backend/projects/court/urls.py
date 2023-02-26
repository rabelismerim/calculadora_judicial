from django.urls import path
from .views import CourtApi

urlpatterns = [

    path('', CourtApi.as_view(), name="court-list-create"),

]