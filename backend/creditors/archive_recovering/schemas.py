from rest_framework import serializers

from core.dttuser.models import User
from creditors.archive_recovering.models import ArchiveRecovering
from projects.abstract_project.schemas import AbstractDescriptionSchema


class ArchiveRecoveringSchema(AbstractDescriptionSchema):
    
    
    class Meta:
        model = ArchiveRecovering
        fields = "__all__"
