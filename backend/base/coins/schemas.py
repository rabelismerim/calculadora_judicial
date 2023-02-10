from base.coins.models import Coins
from base.schemas import AbstractDescriptionSchema


class CoinsSchema(AbstractDescriptionSchema):

    class Meta:
        model = Coins
        fields = "__all__"
