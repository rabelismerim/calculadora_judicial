"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from config.settings import TEMPLATE_FILE_TYPES

from core.abstract.models import AbstractModel

class SheetsTemplate(AbstractModel):
    """
    Class that defines a model for template SheetsFile.

    Attributes:
    ----------
    name : Sheet name
    file : Sheet file of the model export
        The sheet name used by consumption at the frontend.

    """
    name = models.CharField(_('Sheet Name file'), max_length=50)
    file = models.FileField(_('Sheet Template file'), upload_to=f'djud/templates/')
    value = models.TextField(_('Json File Value'), null=True)

    def __str__(self):
        return str(_("sheet: {} | file: {}").format(self.sheet, self.file.name))

    def save(self, *args, **kwargs):
        file_type = self.file.name.split('.')[-1]
        if file_type not in TEMPLATE_FILE_TYPES:
            raise serializers.ValidationError([_('Invalid file type')])
        super(SheetFile, self).save(*args, **kwargs)

    def get_excel_to_json(self):
        rows = pd.read_excel(self.file.open())
        value = []

        if len(rows) == 0:
            return value

        value = rows.to_json()
        return value

    @property
    def filename(self):
        return self.file.name.split("/")[-1]

    @property
    def index(self):
        return self.name.index

