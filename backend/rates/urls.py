from django.urls import path

from rates.views import RateApi, RateFileApi, TemplateApi, TemplateDetailApi

urlpatterns = [

    path('', RateApi.as_view(), name="rate-list-create"),
    path('templates/', TemplateApi.as_view(), name="template-list"),
    path('templates/<uuid:id>/', TemplateDetailApi.as_view(), name="template-detail"),
    path('file/', RateFileApi.as_view(), name="ratefile-list-create"),

]
