from rest_framework import serializers

from core.dttuser.models import User
from creditors.classes.models import Classes


class ClassesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Classes
        fields = "__all__"
    



