from django.urls import include, path

from projects.views import ProjectApi, ProjectDetailApi, AbstractProjectApi


urlpatterns = [
    path('', ProjectApi.as_view(), name="projects-list-create"),
    path('<uuid:id>', ProjectDetailApi.as_view(), name="project-detail"),
    path('judge', include("projects.judge.urls")),
    path('lawyer', include("projects.lawyer.urls")),
    path('region', include("projects.region.urls")),
    path('court', include("projects.court.urls")),
    # path('engagement', include("projects.engagement.urls")),
    path('project_user', include("projects.project_user.urls")),
]
