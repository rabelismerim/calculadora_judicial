from rest_framework import serializers

from core.dttuser.models import User
from creditors.budgets.models import Budgets

class BudgetsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Budgets
        fields = "__all__"
    



