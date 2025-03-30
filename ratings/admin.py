# ratings/admin.py - FULL FILE
from django.contrib import admin
from .models import RatingTier, Flag, Game, CriticReview

@admin.register(RatingTier)
class RatingTierAdmin(admin.ModelAdmin):
    list_display = ('tier_code', 'icon_name', 'display_name', 'color_hex', 'order')
    ordering = ('order',)
    fields = ('tier_code', 'icon_name', 'display_name', 'color_hex', 'description', 'order')
    readonly_fields = ('tier_code',)

@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'description')
    search_fields = ('symbol', 'description')

@admin.register(CriticReview)
class CriticReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer_name', 'score', 'review_url')
    search_fields = ('reviewer_name', 'summary')
    list_filter = ('reviewer_name',)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'rating_tier', 'requires_adjustment', 'developer', 'publisher', 'date_updated')
    list_filter = ('rating_tier', 'requires_adjustment', 'developer', 'publisher') # Added adjustment filter
    search_fields = ('title', 'developer', 'publisher', 'summary')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('flags', 'critic_reviews')
    date_hierarchy = 'date_added'
    ordering = ('-date_updated',)
    # Make slugs read-only as they are auto-generated
    readonly_fields = ('developer_slug', 'publisher_slug', 'date_added', 'date_updated')

    fieldsets = (
        ('Core Information', {
            'fields': ('title', 'slug', 'cover_image_url',
                       ('developer', 'developer_slug'),
                       ('publisher', 'publisher_slug'),
                       'release_date', 'summary')
        }),
        ('Overall Rating & Flags', {
            'fields': ('rating_tier', 'requires_adjustment', 'flags', 'rationale', 'has_spoilers_in_details')
        }),
        ('Additional Info', {
             'classes': ('collapse',),
             'fields': ('adjustment_guide', 'steam_link', 'epic_link', 'gog_link', 'other_store_link',
                        'critic_reviews') # <-- ADD critic_reviews field here
        }),
        ('Detailed IEGS Breakdown', {
            'classes': ('collapse',),
            'fields': (
                ('aqidah_severity', 'aqidah_details', 'aqidah_reason'),
                ('violence_severity', 'violence_details', 'violence_reason'),
                ('immorality_severity', 'immorality_details', 'immorality_reason'),
                ('substances_gambling_severity', 'substances_gambling_details', 'substances_gambling_reason'),
                ('audio_music_severity', 'audio_music_details', 'audio_music_reason'),
                ('time_addiction_severity', 'time_addiction_details', 'time_addiction_reason'),
                ('online_conduct_severity', 'online_conduct_details', 'online_conduct_reason'),
            )
        }),
    )