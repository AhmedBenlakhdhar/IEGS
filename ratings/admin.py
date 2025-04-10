# ratings/admin.py
from django.contrib import admin, messages
from django.urls import reverse
from modeltranslation.admin import TranslationAdmin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # Not needed unless customizing User admin
from django.contrib.auth.models import User
from .models import RatingTier, Flag, Game, CriticReview, GameComment, MethodologyPage, WhyMGCPage
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

@admin.register(RatingTier)
class RatingTierAdmin(TranslationAdmin):
    list_display = ('display_name', 'icon_name', 'color_hex', 'order', 'tier_code')
    list_display_links = ('display_name',)
    ordering = ('order',)

@admin.register(Flag)
class FlagAdmin(TranslationAdmin):
    list_display = ('description', 'symbol')
    list_display_links = ('description',)
    search_fields = ('symbol', 'description')
    ordering = ('description',)

@admin.register(CriticReview)
class CriticReviewAdmin(TranslationAdmin):
    list_display = ('reviewer_name', 'score', 'review_url', 'summary')
    search_fields = ('reviewer_name', 'summary')
    list_filter = ('reviewer_name',)

@admin.register(Game)
class GameAdmin(TranslationAdmin):
    list_display = ('title', 'get_rating_tier_display_name', 'developer', 'publisher', 'date_updated')
    list_filter = ('rating_tier', 'developer', 'publisher')
    search_fields = ('title', 'developer', 'publisher', 'summary', 'rationale')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('critic_reviews',)
    date_hierarchy = 'date_added'
    ordering = ('-date_updated',)
    readonly_fields = ('developer_slug', 'publisher_slug', 'date_added', 'date_updated', 'get_rating_tier_display_name') # Removed get_flags_display

    fieldsets = (
        (_('Core Information'), {
            'fields': ('title', 'slug', 'cover_image_url', ('developer', 'developer_slug'), ('publisher', 'publisher_slug'), 'release_date', 'summary')
        }),
        (_('Platform Availability'), {
            'classes': ('collapse',),
            'fields': (('available_pc', 'available_ps5', 'available_ps4'), ('available_xbox_series', 'available_xbox_one', 'available_switch'), ('available_android', 'available_ios', 'available_quest'))
        }),
        (_('Store Links'), {
            'classes': ('collapse',),
            'fields': ('steam_link', 'epic_link', 'gog_link', 'other_store_link')
        }),
        (_('Overall Rating & General Info'), {
            'fields': (
                'get_rating_tier_display_name', # Show display name (readonly)
                # Removed flags display field
                'rationale',
                'has_spoilers_in_details',
            )
        }),
        (_('Critic Reviews'), {
             'classes': ('collapse',),
             'fields': ('critic_reviews',)
        }),
        # --- Detailed MGC Breakdown Fieldsets ---
        (_('1. Aqidah & Ideology Violations'), {
            'classes': ('collapse', 'wide'),
            'fields': (
                ('forced_shirk_severity', 'forced_shirk_details', 'forced_shirk_reason'),
                ('promote_shirk_severity', 'promote_shirk_details', 'promote_shirk_reason'),
                ('insult_islam_severity', 'insult_islam_details', 'insult_islam_reason'),
                ('depict_unseen_severity', 'depict_unseen_details', 'depict_unseen_reason'),
                ('magic_sorcery_severity', 'magic_sorcery_details', 'magic_sorcery_reason'),
                ('contradictory_ideologies_severity', 'contradictory_ideologies_details', 'contradictory_ideologies_reason'),
            )
        }),
        (_('2. Haram Actions & Scenes'), {
            'classes': ('collapse', 'wide'),
            'fields': (
                ('nudity_lewdness_severity', 'nudity_lewdness_details', 'nudity_lewdness_reason'),
                ('music_instruments_severity', 'music_instruments_details', 'music_instruments_reason'),
                ('gambling_severity', 'gambling_details', 'gambling_reason'),
                ('lying_severity', 'lying_details', 'lying_reason'),
            )
        }),
        (_('3. Simulation & Normalization of Prohibitions'), {
            'classes': ('collapse', 'wide'),
            'fields': (
                ('simulate_killing_severity', 'simulate_killing_details', 'simulate_killing_reason'),
                ('simulate_theft_crime_severity', 'simulate_theft_crime_details', 'simulate_theft_crime_reason'),
                ('normalize_haram_rels_severity', 'normalize_haram_rels_details', 'normalize_haram_rels_reason'),
                ('normalize_substances_severity', 'normalize_substances_details', 'normalize_substances_reason'),
                ('profanity_obscenity_severity', 'profanity_obscenity_details', 'profanity_obscenity_reason'),
            )
        }),
        (_('4. Game-Related Effects, Environment & Risks'), {
            'classes': ('collapse', 'wide'),
            'fields': (
                ('time_wasting_severity', 'time_wasting_details', 'time_wasting_reason'),
                ('financial_extravagance_severity', 'financial_extravagance_details', 'financial_extravagance_reason'),
                ('online_communication_severity', 'online_communication_details', 'online_communication_reason'),
                ('ugc_risks_severity', 'ugc_risks_details', 'ugc_risks_reason'),
            )
        }),
    )

    @admin.display(description=_('Overall Rating Tier'))
    def get_rating_tier_display_name(self, obj):
        return obj.rating_tier.display_name if obj.rating_tier else '-'

    # Removed get_flags_display method

# --- GameCommentAdmin (Corrected Formatting) ---
@admin.register(GameComment)
class GameCommentAdmin(admin.ModelAdmin):
    list_display = ('game', 'user_link', 'created_date', 'approved', 'moderator_attention_needed', 'flag_count_display', 'content_preview')
    list_filter = ('approved', 'moderator_attention_needed', 'created_date', 'game')
    search_fields = ('content', 'user__username', 'game__title')
    actions = ['approve_comments', 'unapprove_comments', 'mark_reviewed', 'deactivate_commenter', 'reactivate_commenter']
    readonly_fields = ('user', 'game', 'created_date', 'flagged_by')
    list_display_links = ('content_preview',)
    fieldsets = (
        (None, {'fields': ('game', 'user', 'created_date')}),
        (_('Content & Status'), {'fields': ('content', 'approved', 'moderator_attention_needed', 'flagged_by')}),
    )

    @admin.display(description=_('User'))
    def user_link(self, obj):
        user_admin_url = reverse("admin:auth_user_change", args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', user_admin_url, obj.user.username)
    user_link.admin_order_field = 'user' # Keep sorting if needed

    @admin.display(description=_('Comment Preview'))
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    @admin.display(description=_('Flags'))
    def flag_count_display(self, obj):
        count = obj.flagged_by.count()
        return count
    # flag_count_display.admin_order_field = 'flag_count' # Cannot sort directly on M2M count without annotation

    @admin.action(description=_('Approve selected comments'))
    def approve_comments(self, request, queryset):
        updated = queryset.update(approved=True)
        self.message_user(request, _(f'{updated} comments were successfully approved.'), messages.SUCCESS)

    @admin.action(description=_('Unapprove selected comments'))
    def unapprove_comments(self, request, queryset):
        updated = queryset.update(approved=False)
        self.message_user(request, _(f'{updated} comments were successfully unapproved.'), messages.SUCCESS)

    @admin.action(description=_('Mark selected comments as reviewed (remove attention flag)'))
    def mark_reviewed(self, request, queryset):
        updated = queryset.update(moderator_attention_needed=False)
        self.message_user(request, _(f'{updated} comments marked as reviewed.'), messages.SUCCESS)

    @admin.action(description=_('Deactivate (Ban) commenter accounts'))
    def deactivate_commenter(self, request, queryset):
        users_to_deactivate = User.objects.filter(pk__in=queryset.values_list('user__pk', flat=True))
        updated_count = users_to_deactivate.update(is_active=False)
        self.message_user(request, _(f'{updated_count} user accounts linked to selected comments were deactivated.'), messages.SUCCESS)

    @admin.action(description=_('Reactivate commenter accounts'))
    def reactivate_commenter(self, request, queryset):
        users_to_reactivate = User.objects.filter(pk__in=queryset.values_list('user__pk', flat=True))
        updated_count = users_to_reactivate.update(is_active=True)
        self.message_user(request, _(f'{updated_count} user accounts linked to selected comments were reactivated.'), messages.SUCCESS)
# --- End GameCommentAdmin ---

@admin.register(MethodologyPage)
class MethodologyPageAdmin(TranslationAdmin):
    list_display = ('title', 'last_updated'); fields = ('title', 'content')

# --- Register WhyMGCPage Admin ---
@admin.register(WhyMGCPage)
class WhyMGCPageAdmin(TranslationAdmin):
    list_display = ('title', 'last_updated')
    fields = ('title', 'content') # Allow editing title and content
