# create_data.py
import json
import random
from django.core.management.base import BaseCommand

from projects.judge.models import Judge
from projects.court.models import Court
from projects.lawyer.models import Lawyer
from projects.project_user.models import ProjectUser
from projects.region.models import Region
from utils import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Get data ids to projetct.'

    def handle(self, *args, **options):
        user_id = str(User.objects.first().id)
        user_id_2 = str(User.objects.last().id)
        user_id_3 = User.objects.exclude(id__in=[user_id, user_id_2]).first()
        user_id_3 = str(user_id_3.id) if user_id_3 else user_id
        data = {
            'judge_id': str(Judge.objects.first().id),
            'region_id': str(Region.objects.first().id),
            'lawyer_id': str(Lawyer.objects.first().id),
            'court_id': str(Court.objects.first().id),
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
                    "archives": [
                        {
                            "archive": {
                                "archive_json": {},
                                "description": "string"
                            }
                        }
                    ],
                    "date_rj_request": "2023-03-02",
                    "date_rj_filing": "2023-03-02",
                    "date_citation": "2023-03-02",
                    "process_number": "string",
                    "status": "E",
                    "competence": "string",
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
            "status": "P",
            "is_adm": True
        }

        print(data)

        with open('project_ids.json', 'w') as f:
            f.write(json.dumps(data))


def cpf_generator():
    cpf = [random.randint(0, 9) for x in range(9)]

    for _ in range(2):
        val = sum([(len(cpf) + 1 - i) * v for i, v in enumerate(cpf)]) % 11

        cpf.append(11 - val if val > 1 else 0)

    return '%s%s%s.%s%s%s.%s%s%s-%s%s' % tuple(cpf)
    return '{}.{}.{}-{}'.format(cpf[0:3], cpf[3:6], cpf[6:9], cpf[9:11])
