from django.contrib import admin

from calculation.verdict.models import TypeCalculation, Verdict, VerdictCalculation

admin.site.register(TypeCalculation)
admin.site.register(Verdict)
admin.site.register(VerdictCalculation)
