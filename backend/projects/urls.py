from django.urls import include, path

from projects.views import ProjectApi, ProjectDetailApi, ProjectCreateApi


urlpatterns = [
    # path('', ProjectApi.as_view(allowed_methods), name="projects-list-create"),
    path('', ProjectApi.as_view(), name="projects-list-create"),
    path('options', ProjectCreateApi.as_view(), name="project-options"),
    path('<uuid:id>', ProjectDetailApi.as_view(), name="project-list-create"),
    path('judge', include("projects.judge.urls")),
    path('lawyer', include("projects.lawyer.urls")),
    path('region', include("projects.region.urls")),
    path('court', include("projects.court.urls")),
    path('engagement', include("projects.engagement.urls")),
    path('project_user', include("projects.project_user.urls")),
]
