from base.schemas import AbstractDescriptionSchema
from recovering.models import Recovering
from rest_framework import serializers


class RecoveringSchema(AbstractDescriptionSchema):

    status_display = serializers.CharField(
        source='get_status_display', read_only=True)

    status_support_display = serializers.CharField(
        source='get_status_support_display', read_only=True)

    class Meta:
        model = Recovering
        fields = "__all__"
