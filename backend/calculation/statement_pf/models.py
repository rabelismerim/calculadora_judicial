"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""

from django.db import models
from calculation.statement.models import Statement
from core.abstract.models import AbstractModel


CHOICES_TOTAL_PF = (('A', 'Total atualizado'), ('D', 'Total devido'))

CHOICES_TAX_DAYS = (('T', 'Taxa SELIC no período'), ('D', 'Dias em atraso'))

CHOICES_DEFAULT_INTEREST_DUE = (
    ('T', 'Total após juros de mora'), ('D', 'Total devido'))


# TODO: somar todas as FundsDescription. Calcular no evento signals.post.save ou em Procedure
class StatementPF(AbstractModel):
    """
    Defines a model for a total value associated with a statement. Inherits from the AbstractModel class,
    which provides common fields such as id, created_at, and updated_at. Contains fields for a field
    description and a total value, as well as a OneToOneField to a Statement object. Subclass this model
    to add specific fields as needed and calculate the total value in the post-save event or a Procedure.
    """
    field_description = models.CharField(
        'Legenda', max_length=1, choices=CHOICES_TOTAL_PF)
    total = models.FloatField('Valor total')
    statement = models.OneToOneField(Statement, on_delete=models.PROTECT)

    def get_recurral_deposit(self):
        if hasattr(self, 'recurraldeposit'):
            return self.recurraldeposit.value
        return 0

    def get_default_interest(self):
        if hasattr(self, 'defaultinterest'):
            return self.defaultinterest.value
        return 0


class AbstractValue(AbstractModel):
    """
    Defines an abstract model for a value associated with a StatementPF object. Inherits from the AbstractModel
    class, which provides common fields such as id, created_at, and updated_at. Contains a value field
    for the associated value, as well as a OneToOneField to a StatementPF object. This class is meant to be
    subclassed to create specific value types associated with a StatementPF object, such as TaxDays,
    RecurralDeposit, DefaultInterest, DefaultInterestDue, TotalDue, and TotalLawyer. The abstract flag
    in the Meta class indicates that this model should not be instantiated directly.
    """
    value = models.FloatField('Valor')
    statement_pf = models.OneToOneField(StatementPF, on_delete=models.PROTECT)

    class Meta:
        abstract = True


# TODO: Tabela estatica. Criar no evento signals.post.save ou em Procedure
class TaxDays(AbstractValue):
    """
    Defines an abstract model for a value associated with a StatementPF object. Inherits from the AbstractModel
    class, which provides common fields such as id, created_at, and updated_at. Contains a value field
    for the associated value, as well as a OneToOneField to a StatementPF object. Subclass this model to add
    specific fields as needed and include a field description for the value type.
    """
    # Taxa SELIC no período, dias em atraso ou EXCLUIR LINHA
    field_description = models.CharField(
        'Legenda', max_length=1, choices=CHOICES_TAX_DAYS)


# TODO: Tabela estatica. Criar no evento signals.post.save ou em Procedure
class RecurralDeposit(AbstractValue):
    """
    Defines an abstract model for a value associated with a StatementPF object. Inherits from the AbstractModel
    class, which provides common fields such as id, created_at, and updated_at. Contains a value field
    for the associated value, as well as a OneToOneField to a StatementPF object. Subclass this model to add
    specific fields as needed and include a field description for the value type.
    """
    # Depósito recursal liberado ou EXCLUIR LINHA


# TODO: Tabela estatica. Criar no evento signals.post.save ou em Procedure
class DefaultInterest(AbstractValue):
    """
    Defines an abstract model for a value associated with a StatementPF object. Inherits from the AbstractModel
    class, which provides common fields such as id, created_at, and updated_at. Contains a value field
    for the associated value, as well as a OneToOneField to a StatementPF object. Subclass this model to add
    specific fields as needed and include a field description for the value type.
    """
    # Juros moratórios ou EXCLUIR LINHA


# TODO: Tabela estatica. Criar no evento signals.post.save ou em Procedure
class DefaultInterestDue(AbstractValue):
    """
    Defines an abstract model for a value associated with a StatementPF object. Inherits from the AbstractModel
    class, which provides common fields such as id, created_at, and updated_at. Contains a value field
    for the associated value, as well as a OneToOneField to a StatementPF object. Subclass this model to add
    specific fields as needed and include a field description for the value type.
    """
    # Total após juros de mora, Total devido ou EXCLUIR LINHA
    field_description = models.CharField(
        'Legenda', max_length=1, choices=CHOICES_DEFAULT_INTEREST_DUE)


# TODO: Tabela estatica. Criar no evento signals.post.save ou em Procedure
class TotalDue(AbstractValue):
    """
    Defines an abstract model for a value associated with a StatementPF object. Inherits from the AbstractModel
    class, which provides common fields such as id, created_at, and updated_at. Contains a value field
    for the associated value, as well as a OneToOneField to a StatementPF object. Subclass this model to add
    specific fields as needed and include a field description for the value type.
    """
    # Total devido ou EXCLUIR LINHA
    field_description = models.CharField(
        'Legenda', max_length=1, choices=CHOICES_DEFAULT_INTEREST_DUE)


# TODO: Tabela estatica. Pegar os valores de TotalValuesFunds ou TotalValuesFundsIntegrations. Criar no evento signals.post.save ou em Procedure
class FundsDescription(AbstractModel):
    """
    This class represents a fund description which includes a description field, a value field,
    and a foreign key to the StatementPF model.

    Attributes:
        field_description (CharField): a field to store the description of the fund.
        value (FloatField): a field to store the value of the fund.
        statement_pf (ForeignKey): a foreign key to the StatementPF model to which the fund description belongs.
    """
    field_description = models.CharField('Descrição', max_length=100)
    value = models.FloatField('Valor')
    statement_pf = models.ForeignKey(StatementPF, on_delete=models.PROTECT)
