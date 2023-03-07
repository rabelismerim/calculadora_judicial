"""
Serializes the fields of the Entity models for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `Entity` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.
"""

import re
from rest_framework import serializers
from base.schemas import AbstractDescriptionSchema
from core.entity.models import Entity


class EntitySchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the EntitySchema model for use in the API.

    This module defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the EntitySchema
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = EntitySchema()
    """

    class Meta:
        model = Entity
        fields = '__all__'

    def __validate_cpf(self, cpf):
        """
        This method is used to validate the cpf variable, which is the Brazilian version of 
        a personal identification number. It checks if the variable is present and has the correct 
        length (11 characters). It also performs numerical calculations with the numbers in the
        variable to check that the information is valid.
        """
        if (not cpf) or (len(cpf) != 11):
            return False
        int_cpf = [int(x) for x in cpf]
        new = int_cpf[:9]
        while len(new) < 11:
            r = sum([(len(new)+1-i)*v for i, v in enumerate(new)]) % 11
            if r > 1:
                f = 11 - r
            else:
                f = 0
            new.append(f)
            if new == int_cpf:
                return True
        return False

    def __validate_cnpj(self, cnpj):
        """
        This method is essentially the same as the one above, but is used to validate the cnpj 
        variable which is the Brazilian version of a business identification number.
        """
        if (not cnpj) or (len(cnpj) != 14):
            return False
        int_cnpj = [int(x) for x in cnpj]
        new = int_cnpj[:12]
        prod = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        while len(new) < 14:
            r = sum([x*y for (x, y) in zip(new, prod)]) % 11
            if r > 1:
                f = 11 - r
            else:
                f = 0
            new.append(f)
            prod.insert(0, 6)
            if new == int_cnpj:
                return True
        return False

    def validate_legal_number(self, legal_number):
        """
        This method uses the two validation methods defined earlier to check for either a valid CPF or 
        CNPJ number, as Brazilian law mandates. If neither of those variables are present, then it throws 
        a ValidationError, otherwise it returns the legal number provided.
        """
        legal_number = ''.join(re.findall(r'\d', str(legal_number)))
        if not self.__validate_cpf(legal_number):
            if not self.__validate_cnpj(legal_number):
                raise serializers.ValidationError(
                    ['CPF/CNPJ inválido'])
        return legal_number
