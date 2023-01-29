from rest_framework import serializers, renderers


class AbstractModelSchema(serializers.Serializer):
    """Serializer AbstractModel fields"""
    renderer_classes = [renderers.JSONRenderer]
    id = serializers.UUIDField(read_only=True)
    create_user = serializers.CharField(source='get_create_user', read_only=True)
    update_user = serializers.CharField(source='get_update_user', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(allow_null=True, read_only=True)

    class Meta:
        fields = '__all__'


class AbstractUpdateModelSchema(AbstractModelSchema):
    """Serializer AbstractModel fields"""

    def get_fields(self):
        fields = super(AbstractUpdateModelSchema, self).get_fields()
        request = self.context.get('request', None)
        if request and getattr(request, 'method', None) == "PUT":
            for key in fields.keys():
                setattr(fields[key], 'required', False)
        return fields
