from django.urls import include, path


urlpatterns = [
    path('project', include("projects.project.urls")),
    path('judge', include("projects.judge.urls")),
    path('layer', include("projects.layer.urls")),
    path('region', include("projects.region.urls")),
]