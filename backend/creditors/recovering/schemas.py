from rest_framework import serializers
from core.dttuser.models import User
from creditors.recovering.models import Recovering
from projects.abstract_project.schemas import AbstractDescriptionSchema


class RecoveringSchema(AbstractDescriptionSchema):
    
   
    class Meta:
        model = Recovering
        fields = "__all__"
