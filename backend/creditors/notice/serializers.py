from rest_framework import serializers

from core.dttuser.models import User
from creditors.notice.models import Notice


class NoticeSerializer(serializers.ModelSerializer):
    
    
    
    class Meta:
        model = Notice
        fields = "__all__"
    



