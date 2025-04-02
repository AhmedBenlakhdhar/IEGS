# ratings/admin.py - FULL FILE (REVISED)
from django.contrib import admin
from .models import RatingTier, Flag, Game, CriticReview
from django.utils.translation import gettext_lazy as _ # <--- Ensure this import is present

@admin.register(RatingTier)
class RatingTierAdmin(admin.ModelAdmin):
    list_display = ('tier_code', 'icon_name', 'display_name', 'color_hex', 'order')
    ordering = ('order',)
    # Use _() for fieldset titles/fields if you define them, otherwise defaults work
    # For simplicity, default field order is often fine here.
    # fields = ('tier_code', 'icon_name', 'display_name', 'color_hex', 'description', 'order')
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
    list_filter = ('rating_tier', 'requires_adjustment', 'developer', 'publisher')
    search_fields = ('title', 'developer', 'publisher', 'summary')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('flags', 'critic_reviews')
    date_hierarchy = 'date_added'
    ordering = ('-date_updated',)
    readonly_fields = ('developer_slug', 'publisher_slug', 'date_added', 'date_updated')

    fieldsets = (
        (_('Core Information'), {
            'fields': ('title', 'slug', 'cover_image_url',
                       ('developer', 'developer_slug'),
                       ('publisher', 'publisher_slug'),
                       'release_date', 'summary')
        }),
        (_('Platform Availability'), {
            'fields': (('available_pc', 'available_ps5', 'available_ps4'), # Group them logically
                       ('available_xbox_series', 'available_xbox_one', 'available_switch'))
        }),
        (_('Store Links'), { # Optional: Group store links
            'classes': ('collapse',),
            'fields': ('steam_link', 'epic_link', 'gog_link', 'other_store_link')
        }),
        (_('Overall Rating & Flags'), {
            'fields': ('rating_tier', 'requires_adjustment', 'flags', 'rationale', 'has_spoilers_in_details')
        }),
        (_('Additional Info'), {
             'classes': ('collapse',),
             'fields': ('adjustment_guide', 'critic_reviews') # Removed store links from here
        }),
        (_('Detailed MGC Breakdown'), {
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
