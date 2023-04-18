from modeltranslation.translator import TranslationOptions, translator

from calculation.premise.models import Premise


class PremiseTranslationOptions(TranslationOptions):
    fields = ('description',)


translator.register(Premise, PremiseTranslationOptions)
