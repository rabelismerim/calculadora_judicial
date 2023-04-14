from django.http import JsonResponse
from rest_framework import permissions, status, serializers
from base.claim.models import ClaimCreditor, ClaimLawyer
from base.claim.schemas import ClaimCreditorUpdateSchema, ClaimLawyerUpdateSchema, ClaimCreditorSchema
from base.coins.models import Coins
from core.abstract.views import AbstractViewApi
from core.permission.views import CheckHasPermission
from creditors.models import Creditor
from creditors.schemas import CreditorSchema
from utils import _, doc

docs = {
    'init': _("""Represents creditor and attorney claims. The `claim` are the `values` and `class` representative of 
    what is being requested. The creditor may have several claims, according to each amount requested. At the end, 
    this claim is used to compare with the calculation of the DTT.
    """),
}


class ClaimCreditorApi(AbstractViewApi):
    """This class provides basic HTTP methods for managing Calculation Objects.
    It includes a serializer_class and required permission_classes to authenticate the users,
    a model instance with a corresponding schema as well as custom query parameters to retrieve data.
    """
    serializer_class = ClaimCreditorSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = ClaimCreditor
    tags=[_("Creditor - Claim")]
    query_params = []
    http_method_names = ['post']
    docs = docs

    @doc("""
        Method to create a new claim for a creditor.
        It validates the serializer data, gets the 'creditor' and 'classes' objects from the input data,
        creates the claim using the model instance and returns a JsonResponse with the serialized 'creditor' object.
        """)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_claim = serializer.validated_data

        creditor_id = new_claim.pop('creditor_id')
        creditor = Creditor.objects.filter(id=creditor_id).first()
        coins = new_claim.get('coins')
        classes = new_claim.get('classes')
        new_claim['coins'] = Coins.objects.create(**coins)
        new_claim['creditor'] = creditor
        self.model.objects.create(classes_id=classes.id, **new_claim)
        return JsonResponse({'creditor': CreditorSchema(creditor).data}, status=status.HTTP_201_CREATED)


class ClaimCreditorUpdateApi(AbstractViewApi):
    """This class provides basic HTTP methods for managing Calculation Objects.
    It includes a serializer_class and required permission_classes to authenticate the users,
    a model instance with a corresponding schema as well as custom query parameters to retrieve data.
    """
    serializer_class = ClaimCreditorUpdateSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = ClaimCreditor
    tags=[_("Creditor - Claim")]
    query_params = []
    http_method_names = ['put']

    @doc("""
        Method to update existing claim for a creditor.
        It validates the serializer data, gets the 'creditor' and 'classes' objects from the input data,
        updates the claim using the model instance and returns a JsonResponse with the serialized 'creditor'
        object.
        """)
    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_claim = serializer.validated_data

        claim_id = kwargs.get('id')
        claim = ClaimCreditor.objects.filter(id=claim_id).first()
        coins = new_claim.pop('coins', None)
        classes = new_claim.pop('classes', None)
        if new_claim:
            claim.dict_update(**new_claim)
        if coins:
            claim.coins.dict_update(**coins)
        if classes and claim.classes != classes:
            claim.classes = classes
            claim.save()

        return JsonResponse({'creditor': CreditorSchema(claim.creditor).data}, status=status.HTTP_201_CREATED)


class ClaimLawyerApi(AbstractViewApi):
    """This class provides basic HTTP methods for managing Calculation Objects.
    It includes a serializer_class and required permission_classes to authenticate the users,
    a model instance with a corresponding schema as well as custom query parameters to retrieve data.
    """
    serializer_class = ClaimLawyerUpdateSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = ClaimLawyer
    tags=[_("Creditor - Claim")]
    query_params = []
    http_method_names = ['post']
    docs = docs

    @doc("""
        Method to create a new claim lawyer for a creditor or update an existing.
        It validates the serializer data, gets the 'creditor' objects from the input data,
        updates or creates the claim using the model instance and returns a JsonResponse with the serialized 'creditor'
        object.
        """)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_claim = serializer.validated_data

        creditor_id = new_claim.pop('creditor_id')
        creditor = Creditor.objects.filter(id=creditor_id).first()
        claim = creditor.get_claim_lawyer()
        coins = new_claim.get('coins')
        classes = new_claim.get('classes')

        if not claim:
            if not coins:
                raise serializers.ValidationError([_('Need to inform the coins')])
            if not classes:
                raise serializers.ValidationError([_('Need to inform the class')])
            new_claim['coins'] = Coins.objects.create(**coins)
            new_claim['creditor'] = creditor
            self.model.objects.create(classes_id=classes.id, **new_claim)
        elif coins:
            claim.coins.dict_update(**coins)

        return JsonResponse({'creditor': CreditorSchema(creditor).data}, status=status.HTTP_201_CREATED)
