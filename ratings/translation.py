# ratings/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import RatingTier, Flag, Game, CriticReview, GameComment, MethodologyPage, WhyMGCPage

@register(RatingTier)
class RatingTierTranslationOptions(TranslationOptions):
    fields = ('display_name', 'description')

@register(Flag)
class FlagTranslationOptions(TranslationOptions):
    fields = ('description',) # Description is now the translatable concern name

@register(CriticReview)
class CriticReviewTranslationOptions(TranslationOptions):
    fields = ('summary',)

@register(Game)
class GameTranslationOptions(TranslationOptions):
    fields = (
        # Core Info
        'title', 'summary', 'rationale',
        # Removed adjustment_guide

        # --- NEW 19 BREAKDOWN FIELDS (Details & Reason) ---
        'forced_shirk_details', 'forced_shirk_reason',
        'promote_shirk_details', 'promote_shirk_reason',
        'insult_islam_details', 'insult_islam_reason',
        'depict_unseen_details', 'depict_unseen_reason',
        'magic_sorcery_details', 'magic_sorcery_reason',
        'contradictory_ideologies_details', 'contradictory_ideologies_reason',
        'nudity_lewdness_details', 'nudity_lewdness_reason',
        'music_instruments_details', 'music_instruments_reason',
        'gambling_details', 'gambling_reason',
        'lying_details', 'lying_reason',
        'simulate_killing_details', 'simulate_killing_reason',
        'simulate_theft_crime_details', 'simulate_theft_crime_reason',
        'normalize_haram_rels_details', 'normalize_haram_rels_reason',
        'normalize_substances_details', 'normalize_substances_reason',
        'profanity_obscenity_details', 'profanity_obscenity_reason',
        'time_wasting_details', 'time_wasting_reason',
        'financial_extravagance_details', 'financial_extravagance_reason',
        'online_communication_details', 'online_communication_reason',
        'ugc_risks_details', 'ugc_risks_reason',
    )

@register(MethodologyPage)
class MethodologyPageTranslationOptions(TranslationOptions):
    fields = ('title', 'content')

@register(WhyMGCPage)
class WhyMGCPageTranslationOptions(TranslationOptions):
    fields = ('title', 'content')