from django.db.models import F
from base.schemas import AbstractChoicesSerializer
from core.abstract.schemas import AbstractModelSchema
from core.dttuser.schemas import UserDttSchema
from projects.court.models import Court
from projects.court.schemas import CourtSchema
from projects.engagement.models import Engagement
from projects.judge.models import Judge
from projects.lawyer.models import Lawyer
from projects.models import STATUS_CHOICES, Project
from rest_framework import serializers
from projects.judge.schemas import JudgeSchema
from projects.lawyer.schemas import LawyerSchema
from projects.project_user.models import ProjectUser
from projects.region.models import Region
from projects.region.schemas import RegionSchema
from projects.engagement.schemas import ProjectEngagementSchema
from recovering.schemas import RecoveringListSchema, RecoveringSchema
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

    engagement = ProjectEngagementSchema(many=False, read_only=True)
    engagements = serializers.ListField(write_only=True)

    # recovering = RecoveringSchema(
    #     many=True, read_only=True, exclude=('project', ))
    recoverings = RecoveringSchema(source='recovering_set',
                                   many=True, read_only=False, exclude=('project', ))

    manager = UserDttSchema(many=False, read_only=True)
    manager_id = serializers.IntegerField(write_only=True)
    partner = UserDttSchema(many=False, read_only=True)
    partner_id = serializers.IntegerField(write_only=True)

    user_names = serializers.ListField(read_only=True)
    users = serializers.ListField(write_only=True, child=UserSerializer())

    status_display = serializers.CharField(
        source='get_status_display', read_only=True)

    num_recovering = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = '__all__'

    def validate_users(self, users):
        if not users:
            raise serializers.ValidationError(
                ['Necessário selecionar ao menos um usuário'])

        if isinstance(users, list) is False:
            raise serializers.ValidationError(
                ['O campo: "users" deve estar no formato de lista'])
        return users

    def validate_engagements(self, engagement_data):

        list_eng = []

        if not engagement_data:
            raise serializers.ValidationError(
                ['Necessário adicionar ao menos um número de engagement'])

        if isinstance(engagement_data, list) is False:
            raise serializers.ValidationError(
                ['O campo: "engagement" deve estar no formato de lista'])

        for engagement_number in engagement_data:
            if Engagement.objects.filter(number=engagement_number).exists():
                raise serializers.ValidationError(
                    ['Número de engagement já cadastrado'])

            list_eng.append(engagement_number)

        return list_eng


class ProjectListSchema(ProjectSchema):
    """Serializer Project fields"""

    # recoverings = RecoveringListSchema(source='recovering_set',
    #                                    many=True, read_only=False, exclude=('project', ))

    class Meta:
        model = Project
        fields = ("id", 'description', 'status',
                  'status_display', 'created_at', 'engagement', 'num_recovering')


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
