from django.urls import include, path

from base.views_historic import UpdateUserApi, TaskStatusApi

urlpatterns = [
    path('historic/<uuid:id>/', UpdateUserApi.as_view(), name="historic"),
    path('task_status/<uuid:id>/', TaskStatusApi.as_view(), name="task-status"),
    path('', include("base.claim.urls")),
    # path('coins/', include("base.coins.urls")),
]
