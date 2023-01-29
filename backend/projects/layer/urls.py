from django.urls import path
from .views import LayerApi

urlpatterns = [

    path('', LayerApi.as_view(), name="layer-list-Create"),

]