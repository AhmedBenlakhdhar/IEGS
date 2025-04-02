# articles/admin.py
from django.contrib import admin
# --- Import TranslationAdmin ---
from modeltranslation.admin import TranslationAdmin
from .models import Article

# --- Inherit from TranslationAdmin ---
@admin.register(Article)
class ArticleAdmin(TranslationAdmin): # Changed from ModelAdmin
    # --- Use original field names ---
    list_display = ('title', 'author_name', 'published_date', 'updated_date')
    search_fields = ('title', 'content', 'author_name')
    # --------------------------------
    prepopulated_fields = {'slug': ('title',)} # May need adjustment based on default lang
    date_hierarchy = 'published_date'
    ordering = ('-published_date',)
    # --- Use original field names ---
    fields = ('title', 'slug', 'header_image_url', 'author_name', 'published_date', 'content')
    # --------------------------------

    # Customize group fieldsets if needed (optional)
    # group_fieldsets = True