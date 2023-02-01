from django.urls import path
from .views import BudgetsSerializer

urlpatterns = [

    path('budgets/<int:budgets_pk>/', BudgetsSerializer.create, name="budgets-create")

]