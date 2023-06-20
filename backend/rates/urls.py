from django.urls import path

from rates.views import RateApi, RateFileApi, TemplateApi, TemplateDetailApi, RateDetailApi, RateValueDetailApi, \
    RateValueDetailUpdateApi

urlpatterns = [
    path('', RateApi.as_view(), name="rate-list-create"),
    path('<uuid:id>/', RateDetailApi.as_view(), name="rate-detail"),
    path('values/', RateValueDetailApi.as_view(), name="rate-values-detail"),
    path('values/<uuid:id>/', RateValueDetailUpdateApi.as_view(), name="rate-values-detail"),
    path('templates/', TemplateApi.as_view(), name="template-list"),
    path('templates/<uuid:id>/', TemplateDetailApi.as_view(), name="template-detail"),
    path('file/', RateFileApi.as_view(), name="ratefile-list-create"),
]
