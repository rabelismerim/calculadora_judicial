from django.contrib import admin

from base.claim.models import ClaimCreditor, ClaimLawyer, Claim

admin.site.register(ClaimCreditor)
admin.site.register(ClaimLawyer)
admin.site.register(Claim)
