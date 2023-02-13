from creditors.classes.schemas import AbstractClassesSchema
from creditors.notice.models import Notice


class NoticeSchema(AbstractClassesSchema):
    model = Notice

    class Meta:
        model = Notice
        exclude = ('creditor', )
