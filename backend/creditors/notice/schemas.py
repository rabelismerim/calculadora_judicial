from creditors.classes.schemas import AbstractClassesSchema
from creditors.notice.models import Notice, NoticeRecovering


class NoticeSchema(AbstractClassesSchema):
    class Meta:
        model = Notice
        exclude = ('creditor',)


class NoticeRecoveringSchema(AbstractClassesSchema):
    class Meta:
        model = NoticeRecovering
        exclude = ('creditor',)
