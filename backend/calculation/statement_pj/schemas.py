"""
Serializes the fields of the StatementPJ model for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `StatementPJ` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.

Usage example:
serializer = StatementPJSchema()
"""

from base.schemas import AbstractDescriptionSchema
from rest_framework import serializers

from calculation.funds.document.schemas import TotalValuesDocumentSchema
from calculation.statement_pj.models import StatementPJ, FundsDocumentDescriptionPJ


class FundsDescriptionPJSchema(AbstractDescriptionSchema):
    """
    A schema class for serializing and deserializing data from the FundsDocumentDescriptionPJ model.

    statement_pj_id: A read-only UUID field representing the ID of the statement.
    funds: A FundsSchema object representing the funds associated with this description, excluding some fields.
    Meta: A class defining the metadata for the FundsDescriptionPJSchema. The model is set to FundsDocumentDescriptionPJ,
    and the statement_pj field is excluded from the schema.
    """
    statement_pj_id = serializers.UUIDField(read_only=True)
    document = TotalValuesDocumentSchema(exclude=('fund_id',), read_only=True)

    class Meta:
        model = FundsDocumentDescriptionPJ
        exclude = ('statement_pj',)


class StatementPJSchema(AbstractDescriptionSchema):
    """
    A schema class for serializing and deserializing data from the StatementPJ model.

    statement_id: A read-only UUID field representing the ID of the statement.
    verbas: A list of FundsDescriptionPJSchema objects representing the fund descriptions associated with this
    statement, excluding the statement_pj_id field.
    """
    statement_id = serializers.UUIDField(read_only=True)
    documents = FundsDescriptionPJSchema(source='get_documents', many=True, read_only=True)

    class Meta:
        model = StatementPJ
        exclude = ('statement',)
