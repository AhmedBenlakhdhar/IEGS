# ratings/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import RatingTier, Flag, Game, CriticReview, GameComment

@register(RatingTier)
class RatingTierTranslationOptions(TranslationOptions):
    fields = ('display_name', 'description')

@register(Flag)
class FlagTranslationOptions(TranslationOptions):
    fields = ('description',)

@register(CriticReview)
class CriticReviewTranslationOptions(TranslationOptions):
    fields = ('summary',) # Only translate the summary quote

@register(Game)
class GameTranslationOptions(TranslationOptions):
    fields = (
        'title',
        'summary',
        'rationale',
        'adjustment_guide',
        'aqidah_details',
        'aqidah_reason',
        'violence_details',
        'violence_reason',
        'immorality_details',
        'immorality_reason',
        'substances_gambling_details',
        'substances_gambling_reason',
        'audio_music_details',
        'audio_music_reason',
        'time_addiction_details',
        'time_addiction_reason',
        'online_conduct_details',
        'online_conduct_reason',
    )
    # Exclude 'slug', 'developer', 'publisher' if they should remain constant

# Note: GameComment content is usually user-generated and might not need modeltranslation
# unless you specifically want admin-translatable comments. Typically, you wouldn't translate user input this way.
# If you needed admin translation for comments (unlikely):
# @register(GameComment)
# class GameCommentTranslationOptions(TranslationOptions):
#     fields = ('content',)