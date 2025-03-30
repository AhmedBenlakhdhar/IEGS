# articles/admin.py
from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_name', 'published_date', 'updated_date')
    search_fields = ('title', 'content', 'author_name')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    ordering = ('-published_date',)
    # Add fields to admin form
    fields = ('title', 'slug', 'header_image_url', 'author_name', 'published_date', 'content') # Added header_image_url
