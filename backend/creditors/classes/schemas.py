from base.coins.schemas import CoinsSchema
from creditors.classes.models import Classes
from base.schemas import AbstractDescriptionSchema
from rest_framework import serializers


class ClassesSchema(AbstractDescriptionSchema):
    classe_display = serializers.CharField(
        source='get_classe_display', read_only=True)

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
    archive_json = serializers.JSONField()
    creditor_id = serializers.UUIDField()

    def validate_creditor_id(self, creditor_id):
        if self.model.objects.filter(creditor_id=creditor_id).exists():
            raise serializers.ValidationError([f'{self.model.__name__} já cadastrado para esse credor'])
        return creditor_id


class AbstractClassesUpdateSchema(AbstractDescriptionSchema):
    classes = ClassesSchema(many=False, read_only=False, required=False)
    coins = CoinsSchema(many=False, read_only=False, required=False)
    archive_json = serializers.JSONField(required=False)
    creditor_id = serializers.UUIDField()


class AbstractClassesLawyerUpdateSchema(AbstractDescriptionSchema):
    coins = CoinsSchema(many=False, read_only=False)
    archive_json = serializers.JSONField()
    creditor_id = serializers.UUIDField()

    def validate(self, data):
        data = super().validate(data)
        classe = '1'
        classes, created = Classes.objects.get_or_create(classe=classe)
        data['classes'] = classes
        return data


class AbstractClassesLawyerSchema(AbstractDescriptionSchema):
    coins = CoinsSchema(many=False, read_only=False, required=False)
    archive_json = serializers.JSONField(required=False)
    creditor_id = serializers.UUIDField()

    def validate_creditor_id(self, creditor_id):
        if self.model.objects.filter(creditor_id=creditor_id).exists():
            raise serializers.ValidationError(
                [f'{self.model.__name__} já cadastrado para esse credor'])
        return creditor_id

    def validate(self, data):
        data = super(AbstractClassesLawyerSchema, self).validate(data)
        classe = '1'
        classes, created = Classes.objects.get_or_create(classe=classe)
        data['classes'] = classes
        return data
