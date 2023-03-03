from django.db.models import F
from base.schemas import AbstractChoicesSerializer
from core.abstract.schemas import AbstractModelSchema
from core.dttuser.schemas import UserDttSchema
from projects.court.models import Court
from projects.court.schemas import CourtSchema
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
from projects.engagement.schemas import ProjectEngagementSchema
from recovering.schemas import RecoveringSchema
from utils import get_user_model
User = get_user_model()


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class ProjectSchema(serializers.ModelSerializer, AbstractModelSchema):
    """Serializer Project fields"""

    judge = JudgeSchema(many=False, read_only=True)
    judge_id = serializers.UUIDField(write_only=True)

    lawyer = LawyerSchema(many=False, read_only=True)
    lawyer_id = serializers.UUIDField(write_only=True)

    region = RegionSchema(many=False, read_only=True)
    region_id = serializers.UUIDField(write_only=True)

    court = CourtSchema(many=False, read_only=True)
    court_id = serializers.UUIDField(write_only=True)

    engagement = ProjectEngagementSchema(
        many=False, exclude=('project_id', 'users'))
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

    # user_names = serializers.ListField(read_only=True)
    users = ProjectUserProjectSchema(
        read_only=True, many=True, source='engagement.users')
    executors = serializers.ListField(write_only=True, child=UserSerializer())
    approvers = serializers.ListField(write_only=True, child=UserSerializer())
    reviewers = serializers.ListField(write_only=True, child=UserSerializer())

    status_display = serializers.CharField(
        source='get_status_display', read_only=True)

    num_recovering = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = '__all__'

    def validate_executors(self, executors):
        if not executors:
            raise serializers.ValidationError(
                ['Necessário selecionar ao menos um usuário'])

        if isinstance(executors, list) is False:
            raise serializers.ValidationError(
                ['O campo executors deve estar no formato de lista'])
        return executors

    def validate_approvers(self, approvers):
        if not approvers:
            raise serializers.ValidationError(
                ['Necessário selecionar ao menos um usuário'])

        if isinstance(approvers, list) is False:
            raise serializers.ValidationError(
                ['O campo approvers deve estar no formato de lista'])
        return approvers

    def validate_reviewers(self, reviewers):
        if not reviewers:
            raise serializers.ValidationError(
                ['Necessário selecionar ao menos um usuário'])

        if isinstance(reviewers, list) is False:
            raise serializers.ValidationError(
                ['O campo reviewers deve estar no formato de lista'])
        return reviewers

    def validate(self, data):
        data = dict(data)
        engagement_data = data.pop('engagement').pop('engagement')
        executors = data.pop('executors', [])
        executors = [x['id'] for x in executors]
        approvers = data.pop('approvers', [])
        approvers = [x['id'] for x in approvers]
        reviewers = data.pop('reviewers', [])
        reviewers = [x['id'] for x in reviewers]
        data['engagement'] = engagement_data
        data['executors'] = executors
        data['approvers'] = approvers
        data['reviewers'] = reviewers
        return super(ProjectSchema, self).validate(data)


class ProjectListSchema(ProjectSchema):
    """Serializer Project fields"""

    # recoverings = RecoveringListSchema(source='recovering_set',
    #                                    many=True, read_only=False, exclude=('project', ))

    class Meta:
        model = Project
        fields = ("id", 'description', 'status',
                  'status_display', 'created_at', 'engagement', 'num_recovering', 'is_adm')


exclude = ('create_user', 'created_at',
           'update_user', 'updated_at')


class ProjectCreateSchema(serializers.Serializer):
    """Serializer Project fields"""

    user_options = UserDttSchema(
        User.objects.all(), many=True, read_only=True, exclude=('create_user', 'created_at', 'is_staff', 'user_permissions', 'date_joined', 'is_active', 'groups'))

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
