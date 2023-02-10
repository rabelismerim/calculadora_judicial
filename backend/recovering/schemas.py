from recovering.models import Recovering
from base.schemas import AbstractDescriptionSchema


class RecoveringSchema(AbstractDescriptionSchema):

    class Meta:
        model = Recovering
        fields = "__all__"
