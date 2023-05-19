from django.db.models import F
from base.schemas import AbstractChoicesSerializer, AbstractDescriptionSchema
from core.abstract.schemas import AbstractModelSchema
from core.dttuser.schemas import UserDttSchema
from projects.court.models import Court
from projects.court.schemas import CourtSchema
from projects.engagement.schemas import ProjectEngagementSchema
from projects.judge.models import Judge
from projects.lawyer.models import Lawyer
from projects.models import STATUS_CHOICES, Project
from rest_framework import serializers
from projects.judge.schemas import JudgeSchema
from projects.lawyer.schemas import LawyerSchema
from projects.project_user.models import ProjectUser
from projects.project_user.schemas import ProjectUserProjectSchema
from projects.region.models import Region
from projects.region.schemas import RegionSchema
from recovering.schemas import RecoveringSchema, RecoveringV2Schema
from utils import get_user_model, _

User = get_user_model()


class UserSerializer(serializers.Serializer):
    """
    Serializes the field id of the UserSerializer for use in the API.

    Usage example:
    serializer = UserSerializer
    """
    id = serializers.IntegerField()


class ProjectRolesSchema(serializers.ModelSerializer, AbstractModelSchema):  # V1
    """
    Serializes the fields of the ProjectSchema model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Project
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = ProjectSchema()
    """

    executors = serializers.ListField(write_only=True, child=UserSerializer())
    approvers = serializers.ListField(write_only=True, child=UserSerializer())
    special_approvers = serializers.ListField(
        write_only=True, child=UserSerializer(), required=False)
    reviewers = serializers.ListField(write_only=True, child=UserSerializer())
    check_list_empty = True

    @staticmethod
    def __get_ids(list_roles):
        return [x['id'] for x in list_roles]

    def validate_executors(self, executors):
        """Validate executors with a list format"""
        if not executors and self.check_list_empty:
            raise serializers.ValidationError(
                [_('Must select at least one user')])

        if isinstance(executors, list) is False:
            raise serializers.ValidationError(
                [_('The executors field must be in list format')])

        return self.__get_ids(executors)

    def validate_approvers(self, approvers):
        """Validate approvers with a list format"""
        if not approvers and self.check_list_empty:
            raise serializers.ValidationError(
                [_('Must select at least one user')])

        if isinstance(approvers, list) is False:
            raise serializers.ValidationError(
                [_('The approvers field must be in list format')])
        return self.__get_ids(approvers)

    def validate_reviewers(self, reviewers):
        """Validate reviewers with a list format"""
        if not reviewers and self.check_list_empty:
            raise serializers.ValidationError(
                [_('Must select at least one user')])

        if isinstance(reviewers, list) is False:
            raise serializers.ValidationError(
                [_('The reviewers field must be in list format')])
        return self.__get_ids(reviewers)

    def validate_special_approvers(self, special_approvers):
        """Validate special_approvers with a list format"""
        if isinstance(special_approvers, list) is False:
            raise serializers.ValidationError(
                [_('The special_approvers field must be in list format')])
        return self.__get_ids(special_approvers)

    class Meta:
        model = Project
        fields = '__all__'


class ProjectSchema(ProjectRolesSchema):  # V1
    """
    Serializes the fields of the ProjectSchema model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Project
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = ProjectSchema()
    """

    judge = JudgeSchema(many=False, read_only=True)
    judge_id = serializers.UUIDField(write_only=True)

    lawyer = LawyerSchema(many=False, read_only=True)
    lawyer_id = serializers.UUIDField(write_only=True)

    region = RegionSchema(many=False, read_only=True)
    region_id = serializers.UUIDField(write_only=True)

    court = CourtSchema(many=False, read_only=True)
    court_id = serializers.UUIDField(write_only=True)

    engagement = ProjectEngagementSchema(
        many=False, exclude=('project_id', 'users', 'user_names'))
    # engagement = serializers.ListField(source='list_engagements')

    # recovering = RecoveringSchema(
    #     many=True, read_only=True, exclude=('project', ))
    recoverings = RecoveringSchema(source='recovering_set',
                                   many=True, read_only=False, exclude=('project_id', 'project'))

    legal_manager = UserDttSchema(many=False, read_only=True)
    legal_manager_id = serializers.IntegerField(write_only=True)

    calculation_manager = UserDttSchema(many=False, read_only=True)
    calculation_manager_id = serializers.IntegerField(write_only=True)

    financial_manager = UserDttSchema(many=False, read_only=True)
    financial_manager_id = serializers.IntegerField(write_only=True)

    legal_partner = UserDttSchema(many=False, read_only=True)
    legal_partner_id = serializers.IntegerField(write_only=True)

    financial_partner = UserDttSchema(many=False, read_only=True)
    financial_partner_id = serializers.IntegerField(write_only=True)

    project_users = ProjectUserProjectSchema(
        read_only=True, many=True, source='engagement.users')
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)
    num_recovering = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = '__all__'

    def validate(self, data):
        """
        Validate the project schema by extracting the necessary data from Project object.
        :param data: Project object.
        :returns: Updated Project object with extracted data.
        """
        data = dict(data)
        engagement_data = data.pop('engagement').pop('engagement')
        data['engagement'] = engagement_data
        return super(ProjectSchema, self).validate(data)


class ProjectV2Schema(ProjectRolesSchema):  # V2
    """
    Serializes the fields of the ProjectSchema model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Project
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = ProjectSchema()
    """

    judge = JudgeSchema(many=False, read_only=True)
    judge_id = serializers.UUIDField(write_only=True)

    lawyer = LawyerSchema(many=False, read_only=True)
    lawyer_id = serializers.UUIDField(write_only=True)

    region = RegionSchema(many=False, read_only=True)
    region_id = serializers.UUIDField(write_only=True)

    court = CourtSchema(many=False, read_only=True)
    court_id = serializers.UUIDField(write_only=True)

    engagement = ProjectEngagementSchema(
        many=False, exclude=('project_id', 'users', 'user_names'))
    recoverings = RecoveringV2Schema(
        source='recovering_set', many=True, read_only=False, fields=('id', 'entity'))

    legal_manager = UserDttSchema(many=False, read_only=True)
    legal_manager_id = serializers.IntegerField(write_only=True)

    calculation_manager = UserDttSchema(many=False, read_only=True)
    calculation_manager_id = serializers.IntegerField(write_only=True)

    financial_manager = UserDttSchema(many=False, read_only=True)
    financial_manager_id = serializers.IntegerField(write_only=True)

    legal_partner = UserDttSchema(many=False, read_only=True)
    legal_partner_id = serializers.IntegerField(write_only=True)

    financial_partner = UserDttSchema(many=False, read_only=True)
    financial_partner_id = serializers.IntegerField(write_only=True)

    project_users = ProjectUserProjectSchema(
        read_only=True, many=True, source='engagement.users')
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)
    num_recovering = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = '__all__'

    def validate(self, data):
        """
        Validate the project schema by extracting the necessary data from Project object.
        :param data: Project object.
        :returns: Updated Project object with extracted data.
        """
        data = dict(data)
        engagement_data = data.pop('engagement').pop('engagement')
        data['engagement'] = engagement_data
        return super(ProjectV2Schema, self).validate(data)


class ProjectListSchema(ProjectSchema):
    """
    Serializes the fields of the Project model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Project
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = ProjectSchema()
    """

    # recoverings = RecoveringListSchema(source='recovering_set',
    #                                    many=True, read_only=False, exclude=('project', ))

    class Meta:
        model = Project
        fields = ("id", 'description', 'status', 'status_display', 'created_at', 'project_users',
                  'engagement', 'num_recovering', 'is_adm', 'process_number', 'legal_manager',
                  'calculation_manager', 'financial_manager', 'legal_partner', 'financial_partner')


class ProjectEditSchema(ProjectRolesSchema):
    """
    Serializes the fields of the Project model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Project
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = ProjectSchema()
    """
    judge_id = serializers.UUIDField(required=False)
    lawyer_id = serializers.UUIDField(required=False)
    region_id = serializers.UUIDField(required=False)
    court_id = serializers.UUIDField(required=False)
    legal_manager_id = serializers.IntegerField(required=False)
    calculation_manager_id = serializers.IntegerField(required=False)
    financial_manager_id = serializers.IntegerField(required=False)
    legal_partner_id = serializers.IntegerField(required=False)
    financial_partner_id = serializers.IntegerField(required=False)

    class Meta:
        model = Project

        fields = ('project_start', 'project_end', 'process_number', 'competence', 'date_rj_request', 'date_rj_filing',
                  'date_citation', 'description', 'judge_id', 'lawyer_id', 'region_id', 'court_id', 'legal_manager_id',
                  'calculation_manager_id', 'financial_manager_id', 'legal_partner_id', 'financial_partner_id',
                  'executors', 'approvers', 'special_approvers', 'reviewers')

    def __init__(self, *args, **kwargs):
        super(ProjectEditSchema, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False


exclude = ('create_user', 'created_at',
           'update_user', 'updated_at')


class ProjectCreateSchema(serializers.Serializer):
    """Serializer Project fields to options to ccreate project"""

    user_options = UserDttSchema(
        User.objects.all(), many=True, read_only=True,
        exclude=('create_user', 'created_at', 'is_staff', 'user_permissions', 'date_joined', 'is_active', 'groups',))

    judge_options = JudgeSchema(Judge.objects.all(),
                                many=True, read_only=True)

    status_options = AbstractChoicesSerializer(
        [{'id': x[0], 'legend': x[1]} for x in STATUS_CHOICES], many=True, read_only=True)

    lawyer_options = LawyerSchema(
        Lawyer.objects.all(), many=True, read_only=True, exclude=exclude)
    region_options = RegionSchema(
        Region.objects.all(), many=True, read_only=True, exclude=exclude)
    court_options = CourtSchema(
        Court.objects.all(), many=True, read_only=True, exclude=exclude)

    project_user_options = ProjectUser.objects.all().values('id', email=F('user__email'), username=F(
        'user__username'), first_name=F('user__first_name'), last_name=F('user__last_name'))
    manager_options = user_options
    partner_options = user_options

    class Meta:
        fields = '__all__'
