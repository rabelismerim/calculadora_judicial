from rest_framework import serializers
from core.dttuser.models import User
from creditors.archive.models import Archive
from projects.abstract_project.schemas import AbstractDescriptionSchema


class ArchiveSchema(AbstractDescriptionSchema):
    
    class Meta:
        model = Archive
        fields = "__all__"
