from django.urls import include, path


urlpatterns = [
    path('budgets', include("creditors.budgets.urls")),
    path('classes', include("creditors.classes.urls")),
    path('notice', include("creditors.notice.urls")),
]
