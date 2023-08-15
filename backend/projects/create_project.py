import random
import secrets

from projects.judge.models import Judge
from projects.court.models import Court
from projects.lawyer.models import Lawyer
from projects.region.models import Region
from utils import get_user_model

User = get_user_model()


def cpf_generator():
    cpf = [secrets.randbelow(10) for _ in range(9)]

    val1 = sum([(len(cpf) + 1 - i) * v for i, v in enumerate(cpf)]) % 11
    cpf.append(11 - val1 if val1 > 1 else 0)

    val2 = sum([(len(cpf) + 1 - i) * v for i, v in enumerate(cpf)]) % 11
    last_digit = 11 - val2 if val2 > 1 else 0
    cpf.append(last_digit if last_digit < 10 else 0)

    return '{}{}{}.{}{}{}.{}{}{}-{}{}'.format(*cpf)

def generate_number():
    return ''.join([str(secrets.randbelow(10)) for _ in range(8)])


def get_data_project(user_id: str = None):
    if not user_id:
        user_id = str(User.objects.first().id)
    user_id_2 = str(User.objects.last().id)
    user_id_3 = User.objects.exclude(id__in=[user_id, user_id_2]).first()
    user_id_3 = str(user_id_3.id) if user_id_3 else user_id
    data = {
        'judge_id': str(Judge.objects.first().id),
        'region_id': str(Region.objects.first().id),
        'lawyer_id': str(Lawyer.objects.first().id),
        'court_id': str(Court.objects.first().id),
        "date_rj_request": "2023-03-02",
        "date_rj_filing": "2023-03-02",
        "date_citation": "2023-03-02",
        "process_number": "string",
        "competence": "string",
        "engagement": {
            "numbers": [
                cpf_generator()
            ]
        },
        "recoverings": [
            {
                "entity": {
                    "name": "string",
                    "legal_number": cpf_generator()
                },
                "status": "E",
                "status_support": "E"
            }
        ],
        "legal_manager_id": user_id,
        "calculation_manager_id": user_id,
        "financial_manager_id": user_id,
        "legal_partner_id": user_id,
        "financial_partner_id": user_id,
        "executors": [
            {
                "id": user_id
            }
        ],
        "approvers": [
            {
                "id": user_id_2
            }
        ],
        "reviewers": [
            {
                "id": user_id_3
            }
        ],
        "description": "string",
        "project_start": "2023-03-02",
        "project_end": "2023-03-02",
        "status": "E",
        "is_adm": True
    }

    return data


def __validate_cpf(cpf):
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
        r = sum([(len(new) + 1 - i) * v for i, v in enumerate(new)]) % 11
        if r > 1:
            f = 11 - r
        else:
            f = 0
        new.append(f)
        if new == int_cpf:
            return True
    return False


print(__validate_cpf(cpf_generator()))
