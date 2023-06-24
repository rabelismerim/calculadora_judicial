"""
Serializes the fields of the Statement models for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `Statement` models to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.
"""
from calculation.statement.models import Lawyer, Statement, TotalLawyer
from base.schemas import AbstractDescriptionSchema
from rest_framework import serializers

from calculation.statement_pf.schemas import StatementPFSchema
from calculation.statement_pj.schemas import StatementPJSchema


class LawyerSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the Lawyer model for use in the API.

    This module defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Lawyer
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = LawyerSchema()
    """

    class Meta:
        model = Lawyer
        exclude = ('total_lawyer',)


class TotalLawyerSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the TotalLawyer model for use in the API.

    This module defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the TotalLawyer
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = TotalLawyerSchema()
    """

    lawyers = LawyerSchema(many=True, source='lawyer_set')

    class Meta:
        model = TotalLawyer
        exclude = ('statement',)


class StatementSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the Statement model for use in the API.

    This module defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Statement
    model to and from JSON format, and validates incoming data based on the model's fields.

    Attributes:
    - statement_pf: A nested serializer that converts instances of the StatementPF
    model to and from JSON format.
    - statement_pj: A nested serializer that converts instances of the StatementPJ
    model to and from JSON format.
    - calculation_id: A read-only UUIDField that represents the calculation object
    associated with the statement.
    - conclusion_display: A CharField that represents the conclusion of the statement.

    Usage example:
    serializer = StatementSchema()
    """
    statement_pf = StatementPFSchema(read_only=True, source='statementpf', exclude=('statement_id',))
    statement_pj = StatementPJSchema(read_only=True, source='statementpj', exclude=('statement_id',))
    lawyer = TotalLawyerSchema(read_only=True, source='totallawyer')
    calculation_id = serializers.UUIDField(read_only=True)
    conclusion_display = serializers.CharField(source='get_conclusion_display')
    total = serializers.CharField(source='total_conclusion', read_only=True)

    class Meta:
        model = Statement
        exclude = ('calculation',)


class UuidListSerializer(serializers.ListSerializer):
    """
    A custom serializer that validates a list of UUIDs.
    """
    child = serializers.UUIDField()


class UuidListField(serializers.ListField):
    """
    A serializer field that expects a list of UUIDs.
    """
    child = serializers.UUIDField()
    list_serializer_class = UuidListSerializer


class StatementUpdateSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the Statement model for use in the API.

    This module defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Statement
    model to and from JSON format, and validates incoming data based on the model's fields.

    Attributes:
    - statement_pf: A nested serializer that converts instances of the StatementPF
    model to and from JSON format.
    - statement_pj: A nested serializer that converts instances of the StatementPJ
    model to and from JSON format.
    - calculation_id: A read-only UUIDField that represents the calculation object
    associated with the statement.
    - conclusion_display: A CharField that represents the conclusion of the statement.

    Usage example:
    serializer = StatementSchema()
    """
    premises = UuidListField()

    class Meta:
        model = Statement
        fields = ('premises',)
