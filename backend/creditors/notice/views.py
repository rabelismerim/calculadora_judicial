from base.coins.models import Coins
from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from core.abstract.views import CustomSchema as AutoSchema
from rest_framework import permissions
from creditors.notice.models import Notice, NoticeRecovering
from creditors.notice.schemas import NoticeSchema, NoticeUpdateSchema, NoticeRecoveringSchema, \
    NoticeRecoveringUpdateSchema
from utils import _, doc


class NoticeApi(AbstractViewApi):
    """HTTP methods for Notice"""
    http_method_names = ['post', 'get']
    serializer_class = NoticeSchema
    permission_classes = [permissions.IsAdminUser]
    model = Notice
    schema = AutoSchema(tags=[str(_("Creditors - Notice"))])

    query_params = []

    docs = {
        'init': _("""NoticeAJ gathers information about the creditor's process. It contains data relevant to the 
        process, such as what was requested by the creditor, how much was calculated due, the dates and amounts."""),
        'get': _("""Get the entire list of notices, containing the classes and values"""),
    }

    @doc("""Create a new NoticeAJ, if it does not exist in the base, if it exists, an exception will be 
        generated.
            Returns NoticeAJ details if successful""")
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_notice = serializer.validated_data
        coins = new_notice.get('coins')
        new_notice['coins'] = Coins.objects.create(**coins)
        notice = self.model.objects.create(**new_notice)
        return JsonResponse({'notice': self.serializer_class(notice, many=False).data}, status=status.HTTP_201_CREATED)


class NoticeUpdateApi(AbstractViewApi):
    """HTTP methods for Notice"""
    http_method_names = ['put']
    serializer_class = NoticeUpdateSchema
    permission_classes = [permissions.IsAdminUser]
    model = Notice
    schema = AutoSchema(tags=[str(_("Creditors - Notice"))])

    query_params = []

    docs = {
        'init': _("""NoticeAJ gathers information about the creditor's process. It contains data relevant to the 
            process, such as what was requested by the creditor, how much was calculated due, the dates and amounts"""),
        'get': _("""Get the entire list of notices, containing the classes and values"""),
    }

    @doc("""
        Method to update existing NoticeAJ for a creditor.
        It validates the serializer data, gets the 'creditor' and 'classes' objects from the input data,
        updates the claim using the model instance and returns a JsonResponse with the serialized 'creditor'
        object.
        """)
    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_notice = serializer.validated_data

        notice_id = kwargs.get('id')
        notice = self.model.objects.filter(id=notice_id).first()
        coins = new_notice.pop('coins', None)
        classes = new_notice.pop('classes', None)
        if new_notice:
            notice.dict_update(**new_notice)
        if coins:
            notice.coins.dict_update(**coins)
        if classes and notice.classes != classes:
            notice.classes = classes
            notice.save()

        return JsonResponse({'creditor': NoticeSchema(notice).data}, status=status.HTTP_201_CREATED)


class NoticeRecoveringApi(AbstractViewApi):
    """HTTP methods for Notice"""
    http_method_names = ['post', 'get']
    serializer_class = NoticeRecoveringSchema
    permission_classes = [permissions.IsAdminUser]
    model = NoticeRecovering
    schema = AutoSchema(tags=[str(_("Creditors - Notice"))])

    query_params = []

    docs = {
        'init': _("""NoticeRecovering gathers information about the creditor's process. It contains data relevant to the 
            process, such as what was requested by the creditor, how much was calculated due, the dates and amounts""")
    }

    @doc("""Create a new NoticeRecovering, if it does not exist in the base, if it exists, an exception will be 
            generated.
                Returns NoticeRecovering details if successful""")
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_notice = serializer.validated_data
        coins = new_notice.get('coins')
        new_notice['coins'] = Coins.objects.create(**coins)
        notice = self.model.objects.create(**new_notice)

        return JsonResponse({'notice': self.serializer_class(notice, many=False).data}, status=status.HTTP_201_CREATED)


class NoticeRecoveringUpdateApi(AbstractViewApi):
    """HTTP methods for Notice"""
    http_method_names = ['put']
    serializer_class = NoticeRecoveringUpdateSchema
    permission_classes = [permissions.IsAdminUser]
    model = NoticeRecovering
    schema = AutoSchema(tags=[str(_("Creditors - Notice"))])

    query_params = []

    docs = {
        'init': _("""NoticeAJ gathers information about the creditor's process. It contains data relevant to the 
                process, such as what was requested by the creditor, how much was calculated due, the dates and 
                amounts"""),
    }

    @doc("""
            Method to update existing NoticeRecovering for a creditor.
            It validates the serializer data, gets the 'creditor' and 'classes' objects from the input data,
            updates the claim using the model instance and returns a JsonResponse with the serialized 'creditor'
            object.
            """)
    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_notice = serializer.validated_data

        notice_id = kwargs.get('id')
        notice = self.model.objects.filter(id=notice_id).first()
        coins = new_notice.pop('coins', None)
        classes = new_notice.pop('classes', None)
        if new_notice:
            notice.dict_update(**new_notice)
        if coins:
            notice.coins.dict_update(**coins)
        if classes and notice.classes != classes:
            notice.classes = classes
            notice.save()

        return JsonResponse({'creditor': NoticeRecoveringSchema(notice).data}, status=status.HTTP_201_CREATED)
