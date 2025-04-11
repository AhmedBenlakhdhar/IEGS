# ratings/admin.py
from django.contrib import admin, messages
from django.urls import reverse
from modeltranslation.admin import TranslationAdmin
from django.contrib.auth.models import User
from .models import RatingTier, Flag, Game, CriticReview, GameComment, MethodologyPage, WhyMGCPage, UserContribution
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

# --- RatingTierAdmin, FlagAdmin, CriticReviewAdmin (Keep as is) ---
@admin.register(RatingTier)
class RatingTierAdmin(TranslationAdmin): list_display = ('display_name', 'icon_name', 'color_hex', 'order', 'tier_code'); list_display_links = ('display_name',); ordering = ('order',)
@admin.register(Flag)
class FlagAdmin(TranslationAdmin): list_display = ('description', 'symbol'); list_display_links = ('description',); search_fields = ('symbol', 'description'); ordering = ('description',)
@admin.register(CriticReview)
class CriticReviewAdmin(TranslationAdmin): list_display = ('reviewer_name', 'score', 'review_url', 'summary'); search_fields = ('reviewer_name', 'summary'); list_filter = ('reviewer_name',)

# --- GameAdmin (REVISED Fieldsets) ---
@admin.register(Game)
class GameAdmin(TranslationAdmin):
    list_display = ('title', 'get_rating_tier_display_name', 'developer', 'publisher', 'date_updated')
    list_filter = ('rating_tier', 'developer', 'publisher')
    search_fields = ('title', 'developer', 'publisher', 'summary', 'rationale')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('critic_reviews',)
    date_hierarchy = 'date_added'
    ordering = ('-date_updated',)
    readonly_fields = ('developer_slug', 'publisher_slug', 'date_added', 'date_updated', 'get_rating_tier_display_name')

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
        (_('Overall Rating & Summary'), { # Renamed section
            'fields': (
                'get_rating_tier_display_name',
                'rationale', # Changed from General Rationale to Rating Summary
            )
        }),
        (_('Critic Reviews'), {
             'classes': ('collapse',),
             'fields': ('critic_reviews',)
        }),
        # --- Detailed MGC Breakdown Fieldsets (Severity ONLY) ---
        (_('1. Aqidah & Ideology Violations'), {
            'classes': ('collapse', 'wide'),
            'fields': (
                'forced_shirk_severity', 'promote_shirk_severity', 'insult_islam_severity',
                'depict_unseen_severity', 'magic_sorcery_severity', 'contradictory_ideologies_severity',
            )
        }),
        (_('2. Haram Actions & Scenes'), {
            'classes': ('collapse', 'wide'),
            'fields': (
                'nudity_lewdness_severity', 'music_instruments_severity',
                'gambling_severity', 'lying_severity',
            )
        }),
        (_('3. Simulation & Normalization of Prohibitions'), {
            'classes': ('collapse', 'wide'),
            'fields': (
                'simulate_killing_severity', 'simulate_theft_crime_severity',
                'normalize_haram_rels_severity', 'normalize_substances_severity',
                'profanity_obscenity_severity',
            )
        }),
        (_('4. Game-Related Effects, Environment & Risks'), {
            'classes': ('collapse', 'wide'),
            'fields': (
                'time_wasting_severity', 'financial_extravagance_severity',
                'online_communication_severity', 'ugc_risks_severity',
            )
        }),
    )

    @admin.display(description=_('Overall Rating Tier'))
    def get_rating_tier_display_name(self, obj):
        return obj.rating_tier.display_name if obj.rating_tier else '-'

@admin.register(GameComment)
class GameCommentAdmin(admin.ModelAdmin):
    list_display = ('game', 'user_link', 'created_date', 'approved', 'moderator_attention_needed', 'flag_count_display', 'content_preview'); list_filter = ('approved', 'moderator_attention_needed', 'created_date', 'game'); search_fields = ('content', 'user__username', 'game__title'); actions = ['approve_comments', 'unapprove_comments', 'mark_reviewed', 'deactivate_commenter', 'reactivate_commenter']; readonly_fields = ('user', 'game', 'created_date', 'flagged_by'); list_display_links = ('content_preview',); fieldsets = ( (None, {'fields': ('game', 'user', 'created_date')}), (_('Content & Status'), {'fields': ('content', 'approved', 'moderator_attention_needed', 'flagged_by')}), );
    @admin.display(description=_('User'))
    def user_link(self, obj): user_admin_url = reverse("admin:auth_user_change", args=[obj.user.pk]); return format_html('<a href="{}">{}</a>', user_admin_url, obj.user.username); user_link.admin_order_field = 'user';
    @admin.display(description=_('Comment Preview'))
    def content_preview(self, obj): return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content;
    @admin.display(description=_('Flags'))
    def flag_count_display(self, obj): return obj.flagged_by.count();
    @admin.action(description=_('Approve selected comments'))
    def approve_comments(self, request, queryset): updated = queryset.update(approved=True); self.message_user(request, _(f'{updated} comments were successfully approved.'), messages.SUCCESS);
    @admin.action(description=_('Unapprove selected comments'))
    def unapprove_comments(self, request, queryset): updated = queryset.update(approved=False); self.message_user(request, _(f'{updated} comments were successfully unapproved.'), messages.SUCCESS);
    @admin.action(description=_('Mark selected comments as reviewed (remove attention flag)'))
    def mark_reviewed(self, request, queryset): updated = queryset.update(moderator_attention_needed=False); self.message_user(request, _(f'{updated} comments marked as reviewed.'), messages.SUCCESS);
    @admin.action(description=_('Deactivate (Ban) commenter accounts'))
    def deactivate_commenter(self, request, queryset): users_to_deactivate = User.objects.filter(pk__in=queryset.values_list('user__pk', flat=True)); updated_count = users_to_deactivate.update(is_active=False); self.message_user(request, _(f'{updated_count} user accounts linked to selected comments were deactivated.'), messages.SUCCESS);
    @admin.action(description=_('Reactivate commenter accounts'))
    def reactivate_commenter(self, request, queryset): users_to_reactivate = User.objects.filter(pk__in=queryset.values_list('user__pk', flat=True)); updated_count = users_to_reactivate.update(is_active=True); self.message_user(request, _(f'{updated_count} user accounts linked to selected comments were reactivated.'), messages.SUCCESS);

# --- REVISED: UserContribution Admin ---
@admin.register(UserContribution)
class UserContributionAdmin(admin.ModelAdmin):
    list_display = ('game', 'user_link', 'get_category_description', 'severity_rating', 'is_spoiler', 'is_approved', 'moderator_attention_needed', 'flag_count_display', 'created_date')
    list_filter = ('is_approved', 'moderator_attention_needed', 'category', 'severity_rating', 'is_spoiler', 'created_date', 'game') # Filter by category FK
    search_fields = ('content', 'user__username', 'game__title', 'category__description', 'category__symbol') # Search by category name/symbol
    actions = ['approve_contributions', 'unapprove_contributions', 'mark_contributions_reviewed', 'deactivate_contributor']
    readonly_fields = ('user', 'game', 'created_date', 'updated_date', 'flagged_by')
    list_display_links = ('get_category_description',) # Link from category description
    fieldsets = (
        (None, {'fields': ('game', 'user', 'created_date', 'updated_date')}),
        (_('Content & Rating'), {'fields': ('category', 'severity_rating', 'content', 'is_spoiler')}), # Use category FK
        (_('Moderation Status'), {'fields': ('is_approved', 'moderator_attention_needed', 'flagged_by')}),
    )
    autocomplete_fields = ['game', 'user', 'category'] # Make selection easier

    @admin.display(description=_('User'))
    def user_link(self, obj): user_admin_url = reverse("admin:auth_user_change", args=[obj.user.pk]); return format_html('<a href="{}">{}</a>', user_admin_url, obj.user.username); user_link.admin_order_field = 'user';
    @admin.display(description=_('Flags'))
    def flag_count_display(self, obj): return obj.flag_count;
    @admin.display(description=_('Category'), ordering='category__description')
    def get_category_description(self, obj): return obj.category.description if obj.category else '-'

    # Keep actions as they are
    @admin.action(description=_('Approve selected contributions'))
    def approve_contributions(self, request, queryset): updated = queryset.update(is_approved=True); self.message_user(request, _(f'{updated} contributions were successfully approved.'), messages.SUCCESS);
    @admin.action(description=_('Unapprove selected contributions'))
    def unapprove_contributions(self, request, queryset): updated = queryset.update(is_approved=False); self.message_user(request, _(f'{updated} contributions were successfully unapproved.'), messages.SUCCESS);
    @admin.action(description=_('Mark selected contributions as reviewed (remove attention flag)'))
    def mark_contributions_reviewed(self, request, queryset): updated = queryset.update(moderator_attention_needed=False); self.message_user(request, _(f'{updated} contributions marked as reviewed.'), messages.SUCCESS);
    @admin.action(description=_('Deactivate (Ban) contributor accounts'))
    def deactivate_contributor(self, request, queryset): users_to_deactivate = User.objects.filter(pk__in=queryset.values_list('user__pk', flat=True)); updated_count = users_to_deactivate.update(is_active=False); self.message_user(request, _(f'{updated_count} user accounts linked to selected contributions were deactivated.'), messages.SUCCESS);

# --- MethodologyPageAdmin & WhyMGCPageAdmin (Keep as is) ---
@admin.register(MethodologyPage)
class MethodologyPageAdmin(TranslationAdmin): list_display = ('title', 'last_updated'); fields = ('title', 'content')
@admin.register(WhyMGCPage)
class WhyMGCPageAdmin(TranslationAdmin): list_display = ('title', 'last_updated'); fields = ('title', 'content')