from rest_framework import serializers

from core.dttuser.models import User
from creditors.recovering.models import Recovering


class RecoveringSerializer(serializers.ModelSerializer):
    
    
    
    class Meta:
        model = Recovering
        fields = "__all__"
    



