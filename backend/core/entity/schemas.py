import re
from rest_framework import serializers
from base.schemas import AbstractDescriptionSchema
from core.entity.models import Entity


class EntitySchema(AbstractDescriptionSchema):
    """Serializer Entity fields"""

    class Meta:
        model = Entity
        fields = '__all__'

    def __validate_cpf(self, cpf):
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
        legal_number = ''.join(re.findall(r'\d', str(legal_number)))
        if not self.__validate_cpf(legal_number):
            if not self.__validate_cnpj(legal_number):
                raise serializers.ValidationError(
                    ['CPF/CNPJ inválido'])

        if Entity.objects.filter(legal_number=legal_number).exists():
            raise serializers.ValidationError(
                ['CPF/CNPJ já cadastrado'])
        return legal_number
