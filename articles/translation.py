# articles/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import Article, ArticleCategory

@register(Article)
class ArticleTranslationOptions(TranslationOptions):
    fields = ('title', 'content', 'author_name')

# --- RESTORE ArticleCategory Registration ---
@register(ArticleCategory)
class ArticleCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')
# ---------------------------------------