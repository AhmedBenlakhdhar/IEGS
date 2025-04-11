# ratings/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import RatingTier, Flag, Game, CriticReview, GameComment, MethodologyPage, WhyMGCPage, UserContribution # Added UserContribution

@register(RatingTier)
class RatingTierTranslationOptions(TranslationOptions): fields = ('display_name', 'description')
@register(Flag)
class FlagTranslationOptions(TranslationOptions): fields = ('description',)
@register(CriticReview)
class CriticReviewTranslationOptions(TranslationOptions): fields = ('summary',)

@register(Game)
class GameTranslationOptions(TranslationOptions):
    fields = (
        # Core Info
        'title', 'summary', 'rationale', # Keep rationale
    )

# Add translations for UserContribution content if desired
@register(UserContribution)
class UserContributionTranslationOptions(TranslationOptions):
    fields = ('content',) # Only content needs translation

@register(MethodologyPage)
class MethodologyPageTranslationOptions(TranslationOptions): fields = ('title', 'content')
@register(WhyMGCPage)
class WhyMGCPageTranslationOptions(TranslationOptions): fields = ('title', 'content')