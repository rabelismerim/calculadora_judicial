from rest_framework import serializers
from core.dttuser.models import User
from creditors.classes.models import Classes
from projects.abstract_project.schemas import AbstractDescriptionSchema


class ClassesSchema(AbstractDescriptionSchema):
    
    class Meta:
        model = Classes
        fields = "__all__"
