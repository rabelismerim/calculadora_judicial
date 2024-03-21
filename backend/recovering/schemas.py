"""
Serializes the fields of the Recovering models for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `Recovering` models to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.
"""

from base.schemas import AbstractDescriptionSchema
from core.entity.schemas import EntitySchema
from creditors.schemas import CreditorSchema
from recovering.models import Recovering
from rest_framework import serializers

from utils import _


class RecoveringSchema(AbstractDescriptionSchema):  # V1
    """
    Serializes the fields of the Lawyer model for use in the API.

    This module defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Lawyer
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = RecoveringSchema()
    """
    entity = EntitySchema(many=False, read_only=False)

    # Arquivos removidos nessa primeira release. Estruturar para subir os arquivos e gerar no front a leitura
    # archive = ArchiveRecoveringSchema(
    #     source='archiverecovering_set', many=True, read_only=True, exclude=('recovering_id', ))
    # archives = ArchiveRecoveringSchema(
    #     many=True, write_only=True, exclude=('recovering_id', ))
    creditors = CreditorSchema(source='creditor_set', many=True, read_only=True, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status_support_display = serializers.CharField(source='get_status_support_display', read_only=True)
    project_id = serializers.UUIDField()

    class Meta:
        model = Recovering
        exclude = ('project',)

    def validate(self, data):
        project_id = data.get('project_id')
        if project_id:
            legal_number = data.get('entity', {}).get('legal_number')
            if Recovering.objects.filter(project_id=project_id, entity__legal_number=legal_number).exists():
                raise serializers.ValidationError([_('Recovering already registered')])
        return super(RecoveringSchema, self).validate(data)


class RecoveringExcelSchema(AbstractDescriptionSchema):
    entity_id = serializers.UUIDField(write_only=True)
    project_id = serializers.UUIDField()

    class Meta:
        model = Recovering
        exclude = ('project', 'entity')


class RecoveringV2Schema(AbstractDescriptionSchema):  # V2
    """
    Serializes the fields of the Lawyer model for use in the API.

    This module defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Lawyer
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = RecoveringSchema()
    """
    entity = EntitySchema(many=False, read_only=False)

    creditors = CreditorSchema(source='creditor_set', many=True, read_only=True, allow_null=True,
                               fields=('id', 'entity'))
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status_support_display = serializers.CharField(source='get_status_support_display', read_only=True)
    project_id = serializers.UUIDField()

    class Meta:
        model = Recovering
        exclude = ('project',)

    def validate(self, data):
        project_id = data.get('project_id')
        if project_id:
            legal_number = data.get('entity', {}).get('legal_number')
            if Recovering.objects.filter(project_id=project_id, entity__legal_number=legal_number).exists():
                raise serializers.ValidationError([_('Recovering already registered')])
        return super(RecoveringV2Schema, self).validate(data)


class RecoveringListSchema(RecoveringSchema):
    """
    Serializes the fields of the Recovering model for use in the API.

    This module defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Recovering
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = RecoveringListSchema()
    """

    class Meta:
        model = Recovering
        fields = ('id', 'entity')
