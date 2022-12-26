from django.urls import include, path


urlpatterns = [

    path('', include("projetos.projeto.api.urls")),

]