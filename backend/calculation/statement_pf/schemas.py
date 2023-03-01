"""
Serializes the fields of the StatementPF model for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `StatementPF` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.

Usage example:
serializer = StatementPFSchema()
"""

from base.schemas import AbstractDescriptionSchema
from rest_framework import serializers

from calculation.statement_pf.models import DefaultInterest, DefaultInterestDue, FundsDescription, RecurralDeposit, StatementPF, TaxDays, AbstractValue, TotalDue


class AbstractValueSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the AbstractValue model for use in the API.

    This module defines a Django REST Framework serializer that inherits from a custom
    `AbstractDescriptionSchema` class. The serializer converts instances of the `AbstractValue`
    model to and from JSON format, and validates incoming data based on the model's fields.

    Attributes:
        - `Meta`: A nested class that specifies metadata for the serializer. The `model`
        attribute specifies the model class that the serializer should be based on, and
        `exclude` lists the fields that should be excluded from the serialized representation.
        `read_only_fields` lists fields that should be included in the serialized representation
        but should not be writable.

    Usage example:
    serializer = AbstractValueSchema()
    """

    statement_pf_id = serializers.UUIDField()

    class Meta:
        model = AbstractValue
        exclude = ('statement_pf', )
        read_only_fields = ('statement_pf', 'statement_pf_id')


class TaxDaysSchema(AbstractValueSchema):
    """
    Serializes the fields of the TaxDays model for use in the API.

    This module defines a Django REST Framework serializer that inherits from a custom
    `AbstractValueSchema` class. The serializer converts instances of the `TaxDays`
    model to and from JSON format, and validates incoming data based on the model's fields.

    Attributes:
        - `Meta`: A nested class that specifies metadata for the serializer. The `model`
        attribute specifies the model class that the serializer should be based on, and
        `exclude` lists the fields that should be excluded from the serialized representation.

    Usage example:
    serializer = TaxDaysSchema()
    """
    field_description_display = serializers.CharField(
        source='get_field_description_display')

    class Meta:
        model = TaxDays
        exclude = ('statement_pf', )


class RecurralDepositSchema(AbstractValueSchema):
    """
    Serializes the fields of the RecurralDeposit model for use in the API.

    This module defines a Django REST Framework serializer that inherits from a custom
    `AbstractValueSchema` class. The serializer converts instances of the `RecurralDeposit`
    model to and from JSON format, and validates incoming data based on the model's fields.

    Attributes:
        - `Meta`: A nested class that specifies metadata for the serializer. The `model`
        attribute specifies the model class that the serializer should be based on, and
        `exclude` lists the fields that should be excluded from the serialized representation.

    Usage example:
    serializer = RecurralDepositSchema()
    """

    class Meta:
        model = RecurralDeposit
        exclude = ('statement_pf', )


class DefaultInterestSchema(AbstractValueSchema):
    """
    Serializes the fields of the DefaultInterest model for use in the API.

    This module defines a Django REST Framework serializer that inherits from a custom
    `AbstractValueSchema` class. The serializer converts instances of the `DefaultInterest`
    model to and from JSON format, and validates incoming data based on the model's fields.

    Attributes:
        - `Meta`: A nested class that specifies metadata for the serializer. The `model`
        attribute specifies the model class that the serializer should be based on, and
        `exclude` lists the fields that should be excluded from the serialized representation.

    Usage example:
    serializer = DefaultInterestSchema()
    """
    class Meta:
        model = DefaultInterest
        exclude = ('statement_pf', )


class DefaultInterestDueSchema(AbstractValueSchema):
    """
    Serializes the fields of the DefaultInterestDue model for use in the API.

    This module defines a Django REST Framework serializer that inherits from both
    `serializers.ModelSerializer` and a custom `AbstractValueSchema` class. The serializer
    converts instances of the `DefaultInterestDue` model to and from JSON format, and
    validates incoming data based on the model's fields.

    Attributes:
        - `Meta`: A nested class that specifies metadata for the serializer. The `model`
          attribute specifies the model class that the serializer should be based on, and
          `exclude` lists the names of all fields that should be excluded from the serialized
          representation. The `field_description_display` attribute specifies the name of
          a field that should be included in the serialized representation using the
          `get_field_description_display()` method.

    Usage example:
    serializer = DefaultInterestDueSchema()
    """
    field_description_display = serializers.CharField(
        source='get_field_description_display')

    class Meta:
        model = DefaultInterestDue
        exclude = ('statement_pf', )


class TotalDueSchema(AbstractValueSchema):
    """
    Serializes the fields of the TotalDue model for use in the API.

    This module defines a Django REST Framework serializer that inherits from both
    `serializers.ModelSerializer` and a custom `AbstractValueSchema` class. The serializer
    converts instances of the `TotalDue` model to and from JSON format, and
    validates incoming data based on the model's fields.

    Attributes:
        - `Meta`: A nested class that specifies metadata for the serializer. The `model`
          attribute specifies the model class that the serializer should be based on, and
          `exclude` lists the names of all fields that should be excluded from the serialized
          representation. The `field_description_display` attribute specifies the name of
          a field that should be included in the serialized representation using the
          `get_field_description_display()` method.

    Usage example:
    serializer = TotalDueSchema()
    """

    field_description_display = serializers.CharField(
        source='get_field_description_display')

    class Meta:
        model = TotalDue
        exclude = ('statement_pf', )


class FundsDescriptionSchema(AbstractValueSchema):
    """
    Serializes the fields of the FundsDescription model for use in the API.

    This module defines a Django REST Framework serializer that inherits from both
    `serializers.ModelSerializer` and a custom `AbstractValueSchema` class. The serializer
    converts instances of the `FundsDescription` model to and from JSON format, and
    validates incoming data based on the model's fields.

    Attributes:
        - `Meta`: A nested class that specifies metadata for the serializer. The `model`
          attribute specifies the model class that the serializer should be based on, and
          `exclude` lists the names of all fields that should be excluded from the serialized
          representation.

    Usage example:
    serializer = FundsDescriptionSchema()
    """
    class Meta:
        model = FundsDescription
        exclude = ('statement_pf', )


class StatementPFSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the StatementPF model for use in the API.

    This module defines a Django REST Framework serializer that inherits from both
    `serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
    converts instances of the `StatementPF` model to and from JSON format, and
    validates incoming data based on the model's fields.

    Attributes:
        - `Meta`: A nested class that specifies metadata for the serializer. The `model`
        attribute specifies the model class that the serializer should be based on, and
        `fields` lists the names of all fields that should be included in the serialized
        representation.

    Usage example:
    serializer = StatementPFSchema()
    """

    statement_id = serializers.UUIDField()

    tax_days = TaxDaysSchema(source='taxdays', exclude=('statement_pf_id', ))

    recurral_deposit = RecurralDepositSchema(
        source='recurraldeposit', exclude=('statement_pf_id', ))

    default_interest = DefaultInterestSchema(
        source='defaultinterest', exclude=('statement_pf_id', ))

    default_interest_due = DefaultInterestDueSchema(
        source='defaultinterestdue', exclude=('statement_pf_id', ))

    total_due = TotalDueSchema(
        source='totaldue', exclude=('statement_pf_id', ))

    funds_description = FundsDescriptionSchema(
        source='fundsdescription_set', exclude=('statement_pf_id', ), many=True)

    field_description_display = serializers.CharField(
        source='get_field_description_display')

    class Meta:
        model = StatementPF
        exclude = ('statement', )
