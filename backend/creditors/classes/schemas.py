from creditors.classes.models import Classes
from base.schemas import AbstractDescriptionSchema


class ClassesSchema(AbstractDescriptionSchema):

    class Meta:
        model = Classes
        fields = "__all__"
