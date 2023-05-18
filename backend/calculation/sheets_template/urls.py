from django.urls import path

from calculation.sheets_template.views import SheetTemplateViewApi

urlpatterns = [
    path('<uuid:calculation_id>/<str:export_type>/', SheetTemplateViewApi.as_view(), name="sheet-template-list"),
]
