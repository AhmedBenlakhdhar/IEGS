# articles/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import Article

@register(Article)
class ArticleTranslationOptions(TranslationOptions):
    fields = ('title', 'content', 'author_name')
    # Exclude 'slug' if you want it generated only from the default language title