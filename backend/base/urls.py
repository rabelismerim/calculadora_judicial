from django.urls import include, path

from base.views_historic import UpdateUserApi

urlpatterns = [
    path('historic/<uuid:id>/', UpdateUserApi.as_view(), name="historic"),
    path('/', include("base.claim.urls")),
    # path('coins/', include("base.coins.urls")),
]
