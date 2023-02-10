from creditors.classes.models import Classes
from base.schemas import AbstractDescriptionSchema


class ClassesSchema(AbstractDescriptionSchema):

    class Meta:
        model = Classes
        fields = "__all__"

    def validate(self, data):
        classe = data.get('classe')
        classes, created = Classes.objects.get_or_create(classe=classe)
        return super(ClassesSchema, self).validate(classes)
