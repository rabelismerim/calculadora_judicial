from django.urls import path
from .views import BudgetsApi


urlpatterns = [
    path('', BudgetsApi.as_view(), name="budgets-list-Create")
]