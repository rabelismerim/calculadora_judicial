from rest_framework import serializers

from core.dttuser.models import User

class UserSerializer(serializers.ModelSerializer):

    full_name = serializers.ReadOnlyField(
        source='get_full_name'
                        )

    class Meta:
        model = User
        fields = ['id', 'username', 'email','full_name']