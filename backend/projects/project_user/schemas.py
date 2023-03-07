"""
This module defines a Schemas classes that provides validators and json parses for managing ProjectUser objects models.
It is extended from an AbstractModelSchema class and includes the fields created_at, updated_at, create_user and update_user.
Schemas classes use the ProjectUser model to work.

Serializes the fields of the ProjectUser model for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `ProjectUser` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.
"""

from core.abstract.schemas import AbstractModelSchema
from rest_framework import serializers
from core.dttuser.schemas import GroupSchema
from projects.project_user.models import ProjectUser


class ProjectUserSchema(AbstractModelSchema):
    """This class serializes fields related to the ProjectUser model, and sets it 
    to read-only for certain fields like 'groups' or 'permissions.'"""
    user = serializers.IntegerField(write_only=True)

    class Meta:
        model = ProjectUser
        fields = '__all__'

        read_only_fields = ('groups', 'permissions', 'id')


class ProjectUserProjectSchema(AbstractModelSchema):
    """
    This class is used to define the schema of the ProjectUser model, by setting some of its attributes, such as groups and read_only_fields.
    An attribute that defines a GroupSchema object which allows it to have many members and have read-only access to certain fields. Excludes the extra fields in the schema: ('permissions', ).
    Defines the meta information of the ProjectUser model. Fields are set to __all__ and exclude is given the field 'user_permissions', while read_only_fileds contain ids and groups. Section of the class where additional information about the class can be included.
    Attribute with the value 'all' which allows for all fields to be included in the class.
    groups = GroupSchema(many=True, read_only=False, exclude=('permissions', ))
    Usage example:
        serializer = ProjectUserProjectSchema()
        Kwargs:
            many=True, read_only=False, exclude=('field_to_exclude', )
    """
    username = serializers.CharField(source='user.username', read_only=True)
    groups = GroupSchema(many=True, read_only=True, exclude=('permissions', ))

    class Meta:
        model = ProjectUser
        fields = '__all__'
        exclude = ('user_permissions', )
        read_only_fields = ('groups', 'user_permissions', 'id')
