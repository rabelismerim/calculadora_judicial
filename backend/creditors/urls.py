from django.urls import include, path


urlpatterns = [
    path('archive', include("creditors.archive.urls")),
    path('archive_recovering', include("creditors.archive_recovering.urls")),
    path('budgets', include("creditors.budgets.urls")),
    path('classes', include("creditors.classes.urls")),
    path('coins', include("creditors.coins.urls")),
    path('notice', include("creditors.notice.urls")),
    path('recovering', include("creditors.recovering.urls")),
]