# ratings/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import (
    RatingTier, Flag, Game, CriticReview, MethodologyPage, WhyMGCPage,
    Suggestion, GameComment, BoycottedEntity
)

@register(RatingTier)
class RatingTierTranslationOptions(TranslationOptions):
    fields = ('display_name', 'description')

@register(Flag) # Flag descriptions (Descriptor names) are translatable
class FlagTranslationOptions(TranslationOptions):
    fields = ('description',)

@register(CriticReview)
class CriticReviewTranslationOptions(TranslationOptions):
    fields = ('summary',) # Only the summary quote needs translation

@register(Game)
class GameTranslationOptions(TranslationOptions):
    fields = (
        # Core translatable fields
        'title',
        'summary', # CONSOLIDATED: Contains overview and rating rationale
        # REMOVED 'guide_for_parents'
        'boycott_reason', # Keep boycott reason translatable
    )
    # Developer/Publisher names are usually not translated.
    # iarc_rating is a code, not translated here.
    # REMOVED alternative_games (M2M field, not directly translated)

# GameComment is NOT translated (user-generated content)
# Suggestion fields are generally NOT translated (user justification, names)
# If justification needed translation, register Suggestion model here.

@register(MethodologyPage)
class MethodologyPageTranslationOptions(TranslationOptions):
    fields = ('title', 'content')

@register(WhyMGCPage)
class WhyMGCPageTranslationOptions(TranslationOptions):
    fields = ('title', 'content')

# BoycottedEntity reason should be translatable
@register(BoycottedEntity)
class BoycottedEntityTranslationOptions(TranslationOptions):
    fields = ('reason',)