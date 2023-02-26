from base.coins.models import Coins
from base.schemas import AbstractDescriptionSchema
from rest_framework import serializers


class CoinsSchema(AbstractDescriptionSchema):
    coin_display = serializers.CharField(
        source='get_coin_display', read_only=True)

    class Meta:
        model = Coins
        fields = "__all__"
