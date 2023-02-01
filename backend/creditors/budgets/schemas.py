from rest_framework import serializers
from core.dttuser.models import User
from creditors.budgets.models import Budgets
from projects.abstract_project.schemas import AbstractDescriptionSchema


class BudgetsSchema(AbstractDescriptionSchema):
    
    class Meta:
        model = Budgets
        fields = "__all__"
