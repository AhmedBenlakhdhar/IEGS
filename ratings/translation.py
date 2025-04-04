# ratings/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import RatingTier, Flag, Game, CriticReview, GameComment, MethodologyPage

@register(RatingTier)
class RatingTierTranslationOptions(TranslationOptions):
    fields = ('display_name', 'description')

@register(Flag)
class FlagTranslationOptions(TranslationOptions):
    fields = ('description',)

@register(CriticReview)
class CriticReviewTranslationOptions(TranslationOptions):
    fields = ('summary',)

@register(Game)
class GameTranslationOptions(TranslationOptions):
    fields = (
        'title', 'summary', 'rationale', 'adjustment_guide',
        # Category 1 (Original names)
        'aqidah_details', 'aqidah_reason',
        # Category 2 (NEW NAMES - must match models.py)
        'haram_depictions_details', 'haram_depictions_reason',
        # Category 3 (NEW NAMES - must match models.py)
        'simulation_haram_details', 'simulation_haram_reason',
        # Category 4 (NEW NAMES - must match models.py)
        'normalization_haram_details', 'normalization_haram_reason',
        # Category 5 (Original names)
        'violence_details', 'violence_reason',
        # Category 6 (Original names)
        'time_addiction_details', 'time_addiction_reason',
        # Category 7 (Original names)
        'online_conduct_details', 'online_conduct_reason',
        # --- Add suitability/positives? Maybe not modeltranslation fields ---
        # 'suitability_notes',
        # 'positive_aspects',
    )

@register(MethodologyPage)
class MethodologyPageTranslationOptions(TranslationOptions):
    fields = ('title', 'content')

# GameComment usually not translated via modeltranslation
