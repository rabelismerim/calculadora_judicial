from base.coins.schemas import CoinsSchema
from calculation.models import Incident
from creditors.classes.models import Classes
from base.schemas import AbstractDescriptionSchema
from rest_framework import serializers

from rates.schemas import RateSchema, TemplateSchema


class IncidentSchema(AbstractDescriptionSchema):
    """
    The IncidentSchema class is a serializer for the Incident model fields. It inherits from the AbstractModelSchema
    class. It includes the following fields:

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


class ClassesSchema(AbstractDescriptionSchema):
    classe_display = serializers.CharField(source='get_classe_display', read_only=True)

    class Meta:
        model = Classes
        fields = "__all__"

    def validate(self, data):
        classe = data.get('classe')
        classes, created = Classes.objects.get_or_create(classe=classe)
        return super(ClassesSchema, self).validate(classes)


class AbstractClassesSchema(AbstractDescriptionSchema):
    classes = ClassesSchema(many=False, read_only=False)
    coins = CoinsSchema(many=False, read_only=False)
    archive_json = serializers.JSONField(allow_null=True, required=False)
    creditor_id = serializers.UUIDField()
    incident_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    incident = IncidentSchema(read_only=True)

    # def validate_creditor_id(self, creditor_id):
    #     if self.model.objects.filter(creditor_id=creditor_id).exists():
    #         raise serializers.ValidationError([f'{self.model.__name__} já cadastrado para esse credor'])
    #     return creditor_id


class AbstractClassesFundsSchema(AbstractDescriptionSchema):
    classes = ClassesSchema(many=False, read_only=False)
    coins = CoinsSchema(many=False, read_only=False)
    archive_json = serializers.JSONField(allow_null=True, required=False)
    # rate_id = serializers.UUIDField(allow_null=True, required=False, write_only=True)
    rate = RateSchema(exclude=('rate_value', 'is_per_day', 'rate_values'), read_only=True)
    template_id = serializers.UUIDField(required=True, write_only=True)
    template = TemplateSchema(read_only=True)
    total = serializers.FloatField(source='get_total_summed', read_only=True)
    incident = serializers.CharField(source='incident__number', read_only=True)
    incident_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        exclude = ('rate',)


class AbstractClassesUpdateSchema(AbstractDescriptionSchema):
    classes = ClassesSchema(many=False, read_only=False, required=False)
    coins = CoinsSchema(many=False, read_only=False, required=False)
    archive_json = serializers.JSONField(allow_null=True, required=False)
    incident_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    incident = IncidentSchema(read_only=True)


class AbstractClassesLawyerUpdateSchema(AbstractDescriptionSchema):
    coins = CoinsSchema(many=False, read_only=False)
    archive_json = serializers.JSONField(allow_null=True, required=False)
    creditor_id = serializers.UUIDField()
    incident_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    incident = IncidentSchema(read_only=True)

    def validate(self, data):
        data = super().validate(data)
        classe = '1'
        classes, created = Classes.objects.get_or_create(classe=classe)
        data['classes'] = classes
        return data


class AbstractClassesLawyerSchema(AbstractDescriptionSchema):
    coins = CoinsSchema(many=False, read_only=False, required=False)
    archive_json = serializers.JSONField(allow_null=True, required=False)
    creditor_id = serializers.UUIDField()
    incident_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    incident = IncidentSchema(read_only=True)

    def validate_creditor_id(self, creditor_id):
        if self.model.objects.filter(creditor_id=creditor_id).exists():
            raise serializers.ValidationError(['{} already registered for this creditor'.format(self.model.__name__)])
        return creditor_id

    def validate(self, data):
        data = super(AbstractClassesLawyerSchema, self).validate(data)
        classe = '1'
        classes, created = Classes.objects.get_or_create(classe=classe)
        data['classes'] = classes
        return data
