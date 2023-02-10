from creditors.notice.models import Notice
from base.schemas import AbstractDescriptionSchema


class NoticeSchema(AbstractDescriptionSchema):

    class Meta:
        model = Notice
        fields = "__all__"
