from modeltranslation.translator import TranslationOptions, translator

from base.models import NatureChoice


class NatureChoiceTranslationOptions(TranslationOptions):
    fields = ('description',)


translator.register(NatureChoice, NatureChoiceTranslationOptions)
