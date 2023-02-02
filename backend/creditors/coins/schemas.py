from rest_framework import serializers
from core.dttuser.models import User
from creditors.coins.models import Coins
from projects.abstract_project.schemas import AbstractDescriptionSchema


class CoinsSchema(AbstractDescriptionSchema):
    
    
    class Meta:
        model = Coins
        fields = "__all__"
