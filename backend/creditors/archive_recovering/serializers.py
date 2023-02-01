from rest_framework import serializers

from core.dttuser.models import User
from creditors.archive_recovering.models import ArchiveRecovering


class ArchiveRecoveringSerializer(serializers.ModelSerializer):
    
    
    
    class Meta:
        model = ArchiveRecovering
        fields = "__all__"
    



