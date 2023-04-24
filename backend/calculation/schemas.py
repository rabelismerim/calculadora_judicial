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
serializer = CalculationSchema()
"""
from django.db.models import Sum, F

from base.schemas import AbstractDescriptionSchema
from calculation.comparative.schemas import ComparativeSchema
from calculation.criterion.schemas import CriterionSchema
from calculation.funds.document.schemas import FundDocumentSchema
from calculation.funds.irrf.schemas import FundIRRFSchema
from calculation.funds.schemas import FundsSchema
from calculation.premise.schemas import PremiseSchema
from calculation.statement.schemas import StatementSchema
from calculation.verdict.schemas import VerdictSchema
from rest_framework import serializers
from calculation.models import Calculation, Incident, CHOICES_STEP
from creditors.classes.models import CLASSE_CHOICES
from creditors.schemas import CreditorSchema


class IncidentSchema(AbstractDescriptionSchema):
    """
    The IncidentSchema class is a serializer for the Incident model fields. It inherits from the AbstractModelSchema class. It includes the following fields:

    creditor: a CreditorSchema instance that is read-only and not serialized.
    creditor_id: a UUIDField instance that is write-only and serialized.
    verdict: a VerdictSchema instance that represents a collection of verdicts related to the Incident.
    criterion: a CriterionSchema instance that is read-only and not serialized.
    funds: a FundsSchema instance that represents a collection of funds related to the Incident.
    statement: a StatementSchema instance that is read-only and not serialized.
    The Meta class is used to specify the Incident model and all fields are serialized.
    The validate method is overridden to handle the verdict_set and funds_set fields and returns the validated data.
    """

    class Meta:
        model = Incident
        fields = '__all__'

    def validate_number(self, number):
        return number


class ClassesSerializer(serializers.Serializer):
    """
   The ClassesSerializer class is used to serialize instances of the Classes model. It includes the following fields:

   classe: A CharField that represents the class related to the objects of the related Calculation instance.
           It is serialized as a string that matches the value of the 'classe' field.
   classe_display: A SerializerMethodField that represents the display version of the class related to the objects
    of the related Calculation instance.
                   It is read-only and automatically serialized as the "display" version of the class.
   """
    classe = serializers.CharField()
    classe_display = serializers.SerializerMethodField('get_classe_display')
    total_value = serializers.FloatField()

    @staticmethod
    def get_classe_display(obj):
        """
        Return the display value of the 'classe' field in Classes model.

        Parameters:
        obj: The Calculation model instance containing the foreign key to Classes model.

        Returns:
        The display value of the 'classe' field specified in the Classes model.
        """
        display_dict = dict(CLASSE_CHOICES)
        return display_dict[obj['classe']]


class CalculationSchema(AbstractDescriptionSchema):
    """
    The CalculationSchema class is a serializer for the Calculation model fields. It inherits from the
     AbstractModelSchema class. It includes the following fields:

    creditor: a CreditorSchema instance that is read-only and not serialized.
    creditor_id: a UUIDField instance that is write-only and serialized.
    verdict: a VerdictSchema instance that represents a collection of verdicts related to the calculation.
    criterion: a CriterionSchema instance that is read-only and not serialized.
    funds: a FundsSchema instance that represents a collection of funds related to the calculation.
    statement: a StatementSchema instance that is read-only and not serialized.
    The Meta class is used to specify the Calculation model and all fields are serialized.
    The validate method is overridden to handle the verdict_set and funds_set fields and returns the validated data.
    """

    incident = IncidentSchema(many=False, read_only=True)
    incident_id = serializers.UUIDField(write_only=True)
    creditor = CreditorSchema(many=False, read_only=True)
    creditor_id = serializers.UUIDField(write_only=True)
    verdict = VerdictSchema(source='verdict_set', many=True, required=False, exclude=('calculation_id',))
    criterion = CriterionSchema(many=False, read_only=True)

    funds = FundsSchema(source='funds_set', many=True,
                        required=False, exclude=('calculation_id',), read_only=True)
    fund_irrf = FundIRRFSchema(source='fundirrf_set', many=True,
                               required=False, exclude=('calculation_id',), read_only=True)
    fund_document = FundDocumentSchema(source='fund_document_set', many=True,
                                       required=False, exclude=('calculation_id',), read_only=True)

    statement = StatementSchema(read_only=True, exclude=('calculation_id',))

    comparative = ComparativeSchema(read_only=True, exclude=('statement_id',))

    step_display = serializers.CharField(source='get_step_display', read_only=True)
    classes = ClassesSerializer(source='get_classes', read_only=True, many=True)
    premises = PremiseSchema(many=True, read_only=True)

    class Meta:
        model = Calculation
        fields = '__all__'
        read_only_fields = ('step', 'number')

    def validate(self, data):
        data['verdict'] = data.pop('verdict_set', None)
        data['funds'] = data.pop('funds_set', None)
        return super(CalculationSchema, self).validate(data)


class ChangeStepSerializer(serializers.Serializer):
    """
    Serializes the field id of the Change Step for use in the API.

    Usage example:
    serializer = ChangeStepSerializer
    """
    next_step = serializers.ChoiceField(source='step', choices=CHOICES_STEP)

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('exclude', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in allowed:
                try:
                    self.fields.pop(field_name)
                except:
                    pass

    def validate(self, data):
        data['next_step'] = data.pop('step')
        return super(ChangeStepSerializer, self).validate(data)
