# articles/admin.py
from django.contrib import admin
# --- Import TranslationAdmin ---
from modeltranslation.admin import TranslationAdmin
from .models import Article, ArticleCategory, ArticleCategoryMembership
from django.utils.translation import gettext_lazy as _

@admin.register(ArticleCategory)
class ArticleCategoryAdmin(TranslationAdmin):
    list_display = ('name', 'slug', 'description')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

# --- Define Inline Admin for the through model ---
class ArticleCategoryMembershipInline(admin.TabularInline):
    model = ArticleCategoryMembership
    extra = 1 # How many extra rows to show
    # Optional: Specify raw_id_fields if you have many categories/articles
    # raw_id_fields = ('articlecategory',)
# ----------------------------------------------


# --- Inherit from TranslationAdmin ---
@admin.register(Article)
class ArticleAdmin(TranslationAdmin):
    list_display = ('title', 'author_name', 'published_date', 'updated_date') # Keep categories_display removed
    search_fields = ('title', 'content', 'author_name') # Keep categories__name removed
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    ordering = ('-published_date',)
    # --- Keep categories removed from fields/filter_horizontal ---
    fields = ('title', 'slug', 'header_image_url', 'author_name', 'published_date', 'content')
    # filter_horizontal = ('categories',) # KEEP REMOVED
    # ----------------------------------------------------
    list_filter = ('published_date',) # Keep categories removed
    # --- Add the Inline ---
    inlines = [ArticleCategoryMembershipInline]
    # ----------------------


    # --- Comment out method ---
    # def categories_display(self, obj):
    #     return ", ".join([category.name for category in obj.categories.all()])
    # categories_display.short_description = _('Categories')
    # -----------------------------------------------