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

from calculation.statement_pf.models import DefaultInterest, DefaultInterestDue, FundsDescription, \
    StatementPF, TaxDays, AbstractValue
from calculation.statement_pj.schemas import FundsDescriptionPJSchema


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
        exclude = ('statement_pf',)
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
    description_display = serializers.CharField(source='get_description_display')

    class Meta:
        model = TaxDays
        exclude = ('statement_pf',)


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
        exclude = ('statement_pf',)


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
          representation. The `description_display` attribute specifies the name of
          a field that should be included in the serialized representation using the
          `get_description_display()` method.

    Usage example:
    serializer = DefaultInterestDueSchema()
    """
    description_display = serializers.CharField(source='get_description_display')

    class Meta:
        model = DefaultInterestDue
        exclude = ('statement_pf',)


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

        fields = ('total', 'description')


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

    # statement_id = serializers.UUIDField()
    # tax_days = TaxDaysSchema(source='taxdays', exclude=('statement_pf_id',))
    # default_interest = DefaultInterestSchema(source='defaultinterest', exclude=('statement_pf_id',))
    # default_interest_due = DefaultInterestDueSchema(source='defaultinterestdue', exclude=('statement_pf_id',))
    # funds_description = FundsDescriptionSchema(source='fundsdescription_set', exclude=('statement_pf_id',), many=True)
    # description_display = serializers.CharField(source='get_description_display')
    # status_display = serializers.CharField(source='get_status_display')
    agreements = FundsDescriptionPJSchema(source='get_agreements', many=True, read_only=True)

    fund = serializers.SerializerMethodField()

    def get_fund(self, obj):
        tax_days = TaxDaysSchema(source='taxdays', exclude=('statement_pf_id',), allow_null=True)
        default_interest = DefaultInterestSchema(source='defaultinterest', exclude=('statement_pf_id',))
        default_interest_due = DefaultInterestDueSchema(source='defaultinterestdue', exclude=('statement_pf_id',))
        funds_description = FundsDescriptionSchema(source='fundsdescription_set', exclude=('statement_pf_id',),
                                                   many=True)

        obj_tax_days = tax_days.to_representation(obj.taxdays) if hasattr(obj, 'taxdays') else None
        obj_defaultinterest = default_interest.to_representation(obj.defaultinterest) if hasattr(obj,
                                                                                                     'defaultinterest') else None
        obj_defaultinterestdue = default_interest_due.to_representation(obj.defaultinterestdue) if hasattr(obj,
                                                                                                       'defaultinterestdue') else None

        return {
            "statement_id": obj.statement_id,
            "tax_days": obj_tax_days,
            "default_interest": obj_defaultinterest,
            "default_interest_due": obj_defaultinterestdue,
            "funds_description": funds_description.to_representation(obj.fundsdescription_set.all()),
            "description_display": obj.get_description_display(),
            "status_display": obj.get_status_display(),
            "status": obj.status,
            "description": obj.description,
            "legend_monetary_correction_update": obj.legend_monetary_correction_update,
            "legend_date_rj_filing_citation": obj.legend_date_rj_filing_citation,
            "total": obj.total,
        }

    class Meta:
        model = StatementPF
        fields = ('fund', 'agreements')
