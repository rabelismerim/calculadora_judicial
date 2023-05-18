from django.urls import path

from rates.views import RateApi, RateFileApi, TemplateApi, TemplateDetailApi, RateDetailApi

urlpatterns = [

    path('', RateApi.as_view(), name="rate-list-create"),
    path('<uuid:id>/', RateDetailApi.as_view(), name="rate-detail"),
    # path('<uuid:id>/', cache_page(60 * 60 * 24 * 7)(RateDetailApi.as_view()), name="rate-detail"),
    path('templates/', TemplateApi.as_view(), name="template-list"),
    path('templates/<uuid:id>/', TemplateDetailApi.as_view(), name="template-detail"),
    path('file/', RateFileApi.as_view(), name="ratefile-list-create"),

]
