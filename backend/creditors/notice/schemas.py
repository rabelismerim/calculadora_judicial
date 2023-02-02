from rest_framework import serializers
from core.dttuser.models import User
from creditors.notice.models import Notice
from projects.abstract_project.schemas import AbstractDescriptionSchema


class NoticeSchema(AbstractDescriptionSchema):
    
    
    class Meta:
        model = Notice
        fields = "__all__"
