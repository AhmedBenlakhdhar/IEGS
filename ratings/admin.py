# ratings/admin.py
from django.contrib import admin
from .models import RatingTier, Flag, Game

@admin.register(RatingTier)
class RatingTierAdmin(admin.ModelAdmin):
    list_display = ('tier_code', 'display_name', 'color_hex', 'order')
    ordering = ('order',)

@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'description')

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'rating_tier', 'developer', 'publisher', 'date_added')
    list_filter = ('rating_tier', 'developer', 'publisher')
    search_fields = ('title', 'summary', 'rationale', 'developer', 'publisher')
    prepopulated_fields = {'slug': ('title',)} # Auto-fill slug based on title
    filter_horizontal = ('flags',) # Better UI for ManyToMany fields
    date_hierarchy = 'date_added'
    ordering = ('-date_added',)