from django.urls import path
from .views import CoinsCreate, addCoins

urlpatterns = [

    path('coins/<int:coins_pk>/', CoinsCreate.as_view(), name="coins-create"),
    path('creditors/coins/', addCoins.as_view(), name="coins-add"),

]