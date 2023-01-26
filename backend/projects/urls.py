from django.urls import include, path


urlpatterns = [

    path('', include("projects.project.urls")),

]