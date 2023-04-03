from creditors.classes.schemas import AbstractClassesSchema, AbstractClassesUpdateSchema
from creditors.notice.models import Notice, NoticeRecovering


class NoticeSchema(AbstractClassesSchema):
    class Meta:
        model = Notice
        exclude = ('creditor',)


class NoticeUpdateSchema(AbstractClassesUpdateSchema):
    class Meta:
        model = Notice
        exclude = ('creditor',)


class NoticeRecoveringSchema(AbstractClassesSchema):
    class Meta:
        model = NoticeRecovering
        exclude = ('creditor',)


class NoticeRecoveringUpdateSchema(AbstractClassesUpdateSchema):
    class Meta:
        model = NoticeRecovering
        exclude = ('creditor',)
