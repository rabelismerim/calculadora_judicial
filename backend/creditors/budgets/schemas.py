from creditors.budgets.models import Budgets
from base.schemas import AbstractDescriptionSchema


class BudgetsSchema(AbstractDescriptionSchema):

    class Meta:
        model = Budgets
        fields = "__all__"
