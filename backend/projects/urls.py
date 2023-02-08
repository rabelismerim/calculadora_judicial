from django.urls import include, path


urlpatterns = [
    path('project', include("projects.project.urls")),
    path('judge', include("projects.judge.urls")),
    path('lawyer', include("projects.lawyer.urls")),
    path('region', include("projects.region.urls")),
    path('engagement', include("projects.engagement.urls")),
    path('project_user', include("projects.project_user.urls")),
]
