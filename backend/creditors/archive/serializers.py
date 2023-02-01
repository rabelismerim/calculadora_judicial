from rest_framework import serializers

from core.dttuser.models import User
from creditors.archive.models import Archive


class ArchiveSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Archive
        fields = "__all__"
    



