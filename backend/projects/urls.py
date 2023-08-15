from django.urls import include, path

from projects.views import ProjectApi, ProjectDetailApi, ProjectDetailV2Api

urlpatterns = [
    path('', ProjectApi.as_view(), name="projects-list-create"),
    path('<uuid:id>/', ProjectDetailApi.as_view(), name="project-detail-v1"),
    path('<uuid:id>/', ProjectDetailV2Api.as_view(), name="project-detail-v2"),
    path('judge/', include("projects.judge.urls")),
    path('lawyer/', include("projects.lawyer.urls")),
    path('region/', include("projects.region.urls")),
    path('court/', include("projects.court.urls")),
    path('engagement/', include("projects.engagement.urls")),
    path('project_user/', include("projects.project_user.urls")),
]
