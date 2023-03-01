"""
Serializes the fields of the Statement model for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `Statement` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.

Usage example:
serializer = StatementSchema()
"""

from calculation.statement.models import Statement
from base.schemas import AbstractDescriptionSchema
from rest_framework import serializers

from calculation.statement_pf.schemas import StatementPFSchema
from calculation.statement_pj.schemas import StatementPJSchema


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
    statement_pf = StatementPFSchema(
        read_only=True, source='statementpf', exclude=('statement_id', ))

    statement_pj = StatementPJSchema(
        read_only=True, source='statementpj', exclude=('statement_id', ))
    calculation_id = serializers.UUIDField(read_only=True)

    conclusion_display = serializers.CharField(source='get_conclusion_display')

    class Meta:
        model = Statement
        exclude = ('calculation', )
