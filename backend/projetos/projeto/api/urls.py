from django.urls import path
from .views import (ProjetoListCreate, ProjetoDetail)

urlpatterns = [

    path('', ProjetoListCreate.as_view(), name="projeto-list-Create"),
    path('<int:pk>', ProjetoDetail.as_view(), name="projeto-detail"),

]