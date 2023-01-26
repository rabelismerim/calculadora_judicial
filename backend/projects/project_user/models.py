from django.db import models
from core.abstract.models import AbstractModel
from utils import get_user_model
from core.dttuser.models import PermissionsMixin


User = get_user_model()


class ProjectUser(AbstractModel, PermissionsMixin):
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return self.user.get_full_name