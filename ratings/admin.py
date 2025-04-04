# ratings/admin.py
from django.contrib import admin, messages
from django.urls import reverse
from modeltranslation.admin import TranslationAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import RatingTier, Flag, Game, CriticReview, GameComment, MethodologyPage
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

# --- Inherit from TranslationAdmin where needed ---

@admin.register(RatingTier)
class RatingTierAdmin(TranslationAdmin): # Changed from ModelAdmin
    # --- Use original field names ---
    list_display = ('tier_code', 'icon_name', 'display_name', 'color_hex', 'order')
    # --------------------------------
    ordering = ('order',)
    readonly_fields = ('tier_code',)

@admin.register(Flag)
class FlagAdmin(TranslationAdmin): # Changed from ModelAdmin
    # --- Use original field names ---
    list_display = ('symbol', 'description')
    search_fields = ('symbol', 'description')
    # --------------------------------

@admin.register(CriticReview)
class CriticReviewAdmin(TranslationAdmin): # Changed from ModelAdmin
    # --- Use original field names ---
    list_display = ('reviewer_name', 'score', 'review_url', 'summary')
    search_fields = ('reviewer_name', 'summary')
    # --------------------------------
    list_filter = ('reviewer_name',)

@admin.register(Game)
class GameAdmin(TranslationAdmin):
    list_display = ('title', 'rating_tier', 'requires_adjustment', 'developer', 'publisher', 'date_updated')
    list_filter = ('rating_tier', 'requires_adjustment', 'developer', 'publisher')
    search_fields = ('title', 'developer', 'publisher', 'summary', 'rationale')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('flags', 'critic_reviews', 'adjustable_flags')
    date_hierarchy = 'date_added'
    ordering = ('-date_updated',)
    readonly_fields = ('developer_slug', 'publisher_slug', 'date_added', 'date_updated')

    fieldsets = (
        (_('Core Information'), {'fields': ('title', 'slug', 'cover_image_url', ('developer', 'developer_slug'), ('publisher', 'publisher_slug'), 'release_date', 'summary')}),
        (_('Platform Availability'), {'fields': (('available_pc', 'available_ps5', 'available_ps4'), ('available_xbox_series', 'available_xbox_one', 'available_switch'), ('available_android', 'available_ios', 'available_quest'))}),
        (_('Store Links'), {'classes': ('collapse',), 'fields': ('steam_link', 'epic_link', 'gog_link', 'other_store_link')}),
        (_('Overall Rating & Flags'), {'fields': ('rating_tier', 'requires_adjustment', 'flags', 'adjustable_flags', 'rationale', 'has_spoilers_in_details')}),
        # --- Consider adding suitability/positives here later ---
        (_('Additional Info'), {'classes': ('collapse',), 'fields': ('adjustment_guide', 'critic_reviews')}),

        # --- UPDATE FIELD NAMES HERE ---
        (_('Detailed MGC Breakdown'), {'classes': ('collapse',), 'fields': (
            # Category 1
            ('aqidah_severity', 'aqidah_details', 'aqidah_reason'),
            # Category 2 (NEW)
            ('haram_depictions_severity', 'haram_depictions_details', 'haram_depictions_reason'),
            # Category 3 (NEW)
            ('simulation_haram_severity', 'simulation_haram_details', 'simulation_haram_reason'),
            # Category 4 (NEW)
            ('normalization_haram_severity', 'normalization_haram_details', 'normalization_haram_reason'),
            # Category 5
            ('violence_severity', 'violence_details', 'violence_reason'),
            # Category 6
            ('time_addiction_severity', 'time_addiction_details', 'time_addiction_reason'),
            # Category 7
            ('online_conduct_severity', 'online_conduct_details', 'online_conduct_reason'),
        )}),
        # --- END UPDATED FIELDS ---
    )

# --- Game Comment Admin (User content - usually NOT translated via modeltranslation) ---
@admin.register(GameComment)
class GameCommentAdmin(admin.ModelAdmin): # Stays as ModelAdmin
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

    def user_link(self, obj):
        user_admin_url = reverse("admin:auth_user_change", args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', user_admin_url, obj.user.username)
    user_link.short_description = _('User')
    user_link.admin_order_field = 'user'

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = _('Comment Preview')

    def flag_count_display(self, obj):
        count = obj.flagged_by.count() # Use related manager count()
        return count
    flag_count_display.short_description = _('Flags')
    # flag_count_display.admin_order_field = 'flag_count' # Requires annotation to sort

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


@admin.register(MethodologyPage)
class MethodologyPageAdmin(TranslationAdmin):
    list_display = ('title', 'last_updated')
    # Automatically uses CKEditor widget for the CKEditorUploadingField
    fields = ('title', 'content') # Simple layout

    # Optional: Prevent adding more than one instance
    # def has_add_permission(self, request):
    #    return not MethodologyPage.objects.exists()
