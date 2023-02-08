from django.contrib import admin

from calculation.verdict.models import TypeCalculation, Verdict

admin.site.register(TypeCalculation)
admin.site.register(Verdict)
