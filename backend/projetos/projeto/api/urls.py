from django.urls import path
from .views import (ProjetoListCreate, ProjetoDetail)

urlpatterns = [

    path('projetos/', ProjetoListCreate.as_view(), name="projeto-list-Create"),
    path('projetos/<int:pk>', ProjetoDetail.as_view(), name="projeto-detail"),

]