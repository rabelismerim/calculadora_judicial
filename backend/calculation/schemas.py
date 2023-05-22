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
from base.schemas import AbstractDescriptionSchema, UpdateUserSerializer
from calculation.comment.schemas import StepCommentSchema, CommentSchema
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
from utils import _


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


class HistoricalSchema(AbstractDescriptionSchema):
    step = StepCommentSchema(source='stepcomment_set', many=True, required=False, read_only=True)
    historical = UpdateUserSerializer(source='get_historical', many=True, read_only=True)

    class Meta:
        model = Calculation
        fields = ('step', 'historical')


class CalculationAllFundsSchema(AbstractDescriptionSchema):  # V1
    """
    The CalculationAllFundsSchema class is a serializer for the Calculation model fields. It inherits from the
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

    all_funds = serializers.SerializerMethodField()

    def get_all_funds(self, obj):
        """
        Serializes all funds, IRRF calculations, and fund documents associated with the given `obj` instance using the Django Rest Framework serializers.

        Args:
            obj: An instance of the model associated with this serializer.

        Returns:
            A list of dictionaries representing the serialized data. Each dictionary contains a `'data'` key, which contains the serialized data, and a `'type'` key, which indicates the type of data ('fund', 'irrf', or 'document').
        """
        return [
            {'data': FundsSchema(many=True, exclude=('calculation_id',), read_only=True).to_representation(
                obj.funds_set.all()), 'type': 'fund'},
            {'data': FundIRRFSchema(many=True, exclude=('calculation_id',), read_only=True).to_representation(
                obj.fundirrf_set.all()), 'type': 'irrf'},
            {'data': FundDocumentSchema(many=True, exclude=('calculation_id',), read_only=True).to_representation(
                obj.funddocument_set.all()), 'type': 'document'}
        ]

    class Meta:
        model = Calculation
        fields = ('all_funds',)


class CalculationSchema(CalculationAllFundsSchema):  # V1
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

    # funds = FundsSchema(source='funds_set', many=True,
    #                     required=False, exclude=('calculation_id',), read_only=True)
    # fund_irrf = FundIRRFSchema(source='fundirrf_set', many=True,
    #                            required=False, exclude=('calculation_id',), read_only=True)
    # fund_document = FundDocumentSchema(source='fund_document_set', many=True,
    #                                    required=False, exclude=('calculation_id',), read_only=True)

    statement = StatementSchema(read_only=True, exclude=('calculation_id',))

    comparative = ComparativeSchema(read_only=True, exclude=('statement_id',))

    step_display = serializers.CharField(source='get_step_display', read_only=True)
    classes = ClassesSerializer(source='get_classes', read_only=True, many=True)
    premises = PremiseSchema(many=True, read_only=True)
    historical = serializers.SerializerMethodField(read_only=True)

    def get_historical(self, obj):
        return HistoricalSchema(obj).data

    class Meta:
        model = Calculation
        fields = '__all__'
        read_only_fields = ('step', 'number', 'approver', 'special_approver', 'executor', 'reviewer')

    def validate(self, data):
        data['verdict'] = data.pop('verdict_set', None)
        data['funds'] = data.pop('funds_set', None)
        data['is_adm'] = data.pop('is_adm', True)
        return super(CalculationSchema, self).validate(data)

    def extract_historical_lists(self, data):
        # Inicializa uma lista para conter os valores históricos
        historical_values = []

        data_copy = data.copy()

        # Percorre as chaves do objeto serializado
        for key in data_copy.keys():
            value = data[key]

            # Se o valor for uma lista e a chave for "historical", adiciona o conteúdo à lista de valores históricos
            if isinstance(value, list) and key == "historical":
                value = data.pop(key)
                historical_values.extend(value)


            # Se o valor for um dicionário, chama recursivamente esta função para verificar se ele contém uma chave "historical"
            elif isinstance(value, dict):
                historical_values.extend(self.extract_historical_lists(value))

                if key == "historical":
                    data.pop(key)

        # Retorna a lista completa de valores históricos encontrados em todo o objeto
        return historical_values

    def to_representation(self, instance):
        self.fields['historical'].context.update({'self': instance})
        data = super().to_representation(instance)
        return data


class CalculationV2Schema(AbstractDescriptionSchema):  # V2
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
    creditor_id = serializers.UUIDField(write_only=True)

    # verdict = VerdictSchema(source='verdict_set', many=True, required=False, exclude=('calculation_id',))
    # criterion = CriterionSchema(many=False, read_only=True)
    # creditor = CreditorSchema(many=False, read_only=True)
    # funds = FundsSchema(source='funds_set', many=True,
    #                     required=False, exclude=('calculation_id',), read_only=True)
    # fund_irrf = FundIRRFSchema(source='fundirrf_set', many=True,
    #                            required=False, exclude=('calculation_id',), read_only=True)
    # fund_document = FundDocumentSchema(source='fund_document_set', many=True,
    #                                    required=False, exclude=('calculation_id',), read_only=True)
    # statement = StatementSchema(read_only=True, exclude=('calculation_id',))
    # comparative = ComparativeSchema(read_only=True, exclude=('statement_id',))

    step_display = serializers.CharField(source='get_step_display', read_only=True)
    classes = ClassesSerializer(source='get_classes', read_only=True, many=True)
    premises = PremiseSchema(many=True, read_only=True)
    historical = serializers.SerializerMethodField(read_only=True)

    def get_historical(self, obj):
        return HistoricalSchema(obj).data

    class Meta:
        model = Calculation
        fields = '__all__'
        read_only_fields = ('step', 'number', 'approver', 'special_approver', 'executor', 'reviewer')

    def validate(self, data):
        data['verdict'] = data.pop('verdict_set', None)
        data['funds'] = data.pop('funds_set', None)
        data['is_adm'] = data.pop('is_adm', True)
        return super(CalculationSchema, self).validate(data)

    def extract_historical_lists(self, data):
        # Inicializa uma lista para conter os valores históricos
        historical_values = []

        data_copy = data.copy()

        # Percorre as chaves do objeto serializado
        for key in data_copy.keys():
            value = data[key]

            # Se o valor for uma lista e a chave for "historical", adiciona o conteúdo à lista de valores históricos
            if isinstance(value, list) and key == "historical":
                value = data.pop(key)
                historical_values.extend(value)


            # Se o valor for um dicionário, chama recursivamente esta função para verificar se ele contém uma chave "historical"
            elif isinstance(value, dict):
                historical_values.extend(self.extract_historical_lists(value))

                if key == "historical":
                    data.pop(key)

        # Retorna a lista completa de valores históricos encontrados em todo o objeto
        return historical_values

    def to_representation(self, instance):
        self.fields['historical'].context.update({'self': instance})
        data = super().to_representation(instance)
        return data


class ChangeStepSerializer(serializers.Serializer):
    """
    Serializes the field id of the Change Step for use in the API.

    Usage example:
    serializer = ChangeStepSerializer
    """
    next_step = serializers.ChoiceField(source='step', choices=CHOICES_STEP)
    comments = CommentSchema(many=True, write_only=True, required=False, exclude=('create_user', 'update_user',))

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('exclude', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in allowed:
                try:
                    self.fields.pop(field_name)
                except KeyError:
                    pass

    def validate(self, data):
        data['next_step'] = data.pop('step')
        return super(ChangeStepSerializer, self).validate(data)


class CheckStepSerializer(serializers.Serializer):
    """
    Serializes the field id of the Change Step for use in the API.

    Usage example:
    serializer = ChangeStepSerializer
    """
    next_step = serializers.ChoiceField(source='step', choices=CHOICES_STEP)



class IdSerializer(serializers.Serializer):
    """
    Serializes the field id of the UserSerializer for use in the API.

    Usage example:
    serializer = UserSerializer
    """
    id = serializers.UUIDField()


class ValidatedIDSchema(serializers.Serializer):  # V1
    """
    Serializes the fields of the ValidatedIDSchema model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Project
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = ValidatedIDSchema()
    """

    calculations = serializers.ListField(write_only=True, child=IdSerializer())

    @staticmethod
    def __get_ids(list_roles):
        return [x['id'] for x in list_roles]

    def validate_calculations(self, calculations):
        """Validate calculations with a list format"""
        if isinstance(calculations, list) is False:
            raise serializers.ValidationError(
                [_('The calculations field must be in list format')])
        return self.__get_ids(calculations)