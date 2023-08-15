from django.db import models
from calculation.models import Calculation
from base.claim.models import Claim
from base.models import AbstractDateCreditor, AbstractDateRecovering
from core.abstract.models import AbstractModel


class Criterion(AbstractDateCreditor, AbstractDateRecovering):
    """
    This class represents a criterion for a creditor's claim. It extends the AbstractDateCreditor class and has a
    OneToOne relationship with the Calculation model. It also includes a ForeignKey to the Claim model to retrieve
    information about the creditor.

    Method: get_claims_creditor
    """

    calculation = models.OneToOneField(Calculation, on_delete=models.PROTECT)
    claim_lawyer = models.ForeignKey(Claim, on_delete=models.PROTECT, null=True, blank=True)  # Pegar informações do credor


def get_claims_creditor(self):
    """
    This method retrieves all claims associated with the criterion's creditor. It returns a list of Claim objects.
    """
    claims_creditor = self.criterionclaimcredor_set.all()
    claims = []
    for claim_creditor in claims_creditor:
        claims.append(claim_creditor.claim_creditor)
    return claims


def __str__(self):
    return f"{self.id} | {str(self.calculation)}"


class CriterionClaimCredor(AbstractModel):
    """
    This class represents the relationship between a Criterion and its related Claims.
    In particular, it associates a Criterion with a Claim submitted by a Creditor.
    """
    criterion = models.ForeignKey(Criterion, on_delete=models.PROTECT)
    claim_creditor = models.ForeignKey(Claim, on_delete=models.PROTECT)  # Pegar informações do credor
