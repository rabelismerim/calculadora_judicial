from rest_framework import serializers

from core.dttuser.models import User
from creditors.coins.models import Coins


class CoinsSerializer(serializers.ModelSerializer):
    
    
    
    class Meta:
        model = Coins
        fields = "__all__"
    



