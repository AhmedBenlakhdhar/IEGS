# ratings/admin.py
from django.contrib import admin, messages
from django.urls import reverse
from modeltranslation.admin import TranslationAdmin
from django.contrib.auth.models import User
from .models import RatingTier, Flag, Game, CriticReview, GameComment, MethodologyPage, WhyMGCPage, Suggestion, BoycottedEntity
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

# --- RatingTierAdmin ---
@admin.register(RatingTier)
class RatingTierAdmin(TranslationAdmin):
    list_display = ('display_name', 'icon_name', 'color_hex', 'order', 'tier_code')
    list_display_links = ('display_name',)
    ordering = ('order',)

# --- FlagAdmin ---
@admin.register(Flag)
class FlagAdmin(TranslationAdmin):
    list_display = ('description', 'symbol')
    list_display_links = ('description',)
    search_fields = ('symbol', 'description')
    ordering = ('description',)
    verbose_name = _('Content Descriptor')
    verbose_name_plural = _('Content Risks')

# --- CriticReviewAdmin ---
@admin.register(CriticReview)
class CriticReviewAdmin(TranslationAdmin):
    list_display = ('reviewer_name', 'score', 'review_url', 'summary')
    search_fields = ('reviewer_name', 'summary')
    list_filter = ('reviewer_name',)

# --- GameAdmin ---
@admin.register(Game)
class GameAdmin(TranslationAdmin):
    list_display = ('title', 'get_final_rating_tier_display', 'developer', 'publisher', 'date_updated', 'display_boycott_status')
    list_filter = ('rating_tier', 'developer', 'publisher', 'is_boycotted')
    search_fields = ('title', 'developer', 'publisher', 'summary', 'boycott_reason')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('critic_reviews',)
    date_hierarchy = 'date_added'
    ordering = ('-date_updated',)
    readonly_fields = (
        'developer_slug', 'publisher_slug', 'date_added', 'date_updated',
        'get_final_rating_tier_display', 'get_assigned_flags_display',
        'display_developer_boycott_status', 'display_publisher_boycott_status'
    )
    fieldsets = (
        (_('Core Information'), {'fields': ('title', 'slug', ('developer', 'developer_slug'), ('publisher', 'publisher_slug'), 'release_date', 'summary')}),
        (_('Boycott Status'), {'fields': ('is_boycotted', 'boycott_reason', 'display_developer_boycott_status', 'display_publisher_boycott_status')}),
        (_('Platform Availability'), {'classes': ('collapse',),'fields': (('available_pc', 'available_ps5', 'available_ps4'), ('available_xbox_series', 'available_xbox_one', 'available_switch'), ('available_android', 'available_ios', 'available_quest'))}),
        (_('Store Links'), {'classes': ('collapse',),'fields': ('steam_link', 'epic_link', 'gog_link', 'other_store_link')}),
        (_('MGC Rating & Content'), {'fields': ('get_final_rating_tier_display', 'get_assigned_flags_display',)}),
        (_('Critic Reviews'), {'classes': ('collapse',),'fields': ('critic_reviews',)}),
        (_('A. Risks to Faith'), {'classes': ('collapse', 'wide'),'description': _("Severity Mapping: Mild -> Doubtful, Moderate -> Haram, Severe -> Kufr/Shirk"),'fields': ( 'distorting_islam_severity', 'promoting_kufr_severity', 'assuming_divinity_severity', 'tampering_ghaib_severity', 'deviant_ideologies_severity',)}),
        (_('B. Prohibition Exposure'), {'classes': ('collapse', 'wide'),'description': _("Severity Mapping: Mild -> Permissible, Moderate -> Doubtful, Severe -> Haram"),'fields': ( 'gambling_severity', 'lying_severity', 'indecency_severity', 'music_instruments_severity', 'time_waste_severity',)}),
        (_('C. Normalization Risks'), {'classes': ('collapse', 'wide'),'description': _("Severity Mapping: Mild -> Permissible, Moderate/Severe -> Doubtful"),'fields': ( 'disdain_arrogance_severity', 'magic_severity', 'intoxicants_severity', 'crime_violence_severity', 'profanity_severity',)}),
        (_('D. Player Risks'), {'classes': ('collapse', 'wide'),'description': _("Severity Mapping: Mild/Moderate -> Permissible, Severe -> Doubtful"),'fields': ( 'horror_fear_severity', 'despair_severity', 'spending_severity', 'online_interactions_severity', 'user_content_severity',)}),
    )

    @admin.display(description=_('Overall Rating Tier'), ordering='rating_tier__order')
    def get_final_rating_tier_display(self, obj):
        return obj.rating_tier.display_name if obj.rating_tier else '-'

    @admin.display(description=_('Assigned Flags'))
    def get_assigned_flags_display(self, obj):
        flags_html = [f'<span class="material-symbols-outlined" title="{flag.description}" style="font-size: 1.2em; vertical-align: -3px; margin-right: 4px;">{flag.symbol}</span>' if flag.symbol else '' for flag in obj.flags.all().order_by('description')]
        return format_html(' '.join(flags_html))

    @admin.display(description=_('Boycott Status'), boolean=True)
    def display_boycott_status(self, obj):
        return obj.show_boycott_notice

    @admin.display(description=_('Developer Boycott Status'))
    def display_developer_boycott_status(self, obj):
        entity = obj._developer_boycott_info
        if entity:
            reason = entity.reason
            entity_name = entity.name
            return format_html('<strong style="color: red;">{} ({})</strong><br>{}',
                               _('Boycotted'), entity_name, reason or _('No reason provided.'))
        return _('Not Boycotted')

    @admin.display(description=_('Publisher Boycott Status'))
    def display_publisher_boycott_status(self, obj):
        entity = obj._publisher_boycott_info
        if entity:
            reason = entity.reason
            entity_name = entity.name
            return format_html('<strong style="color: red;">{} ({})</strong><br>{}',
                               _('Boycotted'), entity_name, reason or _('No reason provided.'))
        return _('Not Boycotted')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


# --- GameCommentAdmin ---
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
    user_link.admin_order_field = 'user'

    @admin.display(description=_('Comment Preview'))
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    @admin.display(description=_('Flags'))
    def flag_count_display(self, obj):
        return obj.flagged_by.count()

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


# --- Suggestion Admin ---
@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('suggestion_type', 'user_display', 'game_display', 'descriptor_display', 'status', 'created_date')
    list_filter = ('status', 'suggestion_type', 'created_date', 'game', 'existing_descriptor')
    search_fields = ('justification', 'user__username', 'game__title', 'existing_descriptor__description', 'suggested_descriptor_name')
    actions = ['mark_approved', 'mark_implemented', 'mark_rejected', 'mark_pending']
    fieldsets = (
        (None, {'fields': ('suggestion_type', 'user', 'game')}),
        (_('Severity Change Details'), {
            'classes': ('collapse',),
            'description': _("These fields are relevant for 'Suggest Severity Change' type."),
            'fields': ('existing_descriptor', 'current_severity', 'suggested_severity')
        }),
         (_('New Descriptor Details'), {
            'classes': ('collapse',),
            'description': _("These fields are relevant for 'Suggest New Descriptor' type."),
            'fields': ('suggested_descriptor_name', 'suggested_descriptor_icon')
        }),
        (_('Justification & Status'), {
            'fields': ('justification', 'status')
        }),
        (_('Timestamps'), {
            'fields': ('created_date', 'updated_date'),
            'classes': ('collapse',)
        }),
    )
    autocomplete_fields = ['user', 'game', 'existing_descriptor']
    readonly_fields = ('created_date', 'updated_date', 'current_severity')

    @admin.display(description=_('User'), ordering='user__username')
    def user_display(self, obj):
        if obj.user:
            user_admin_url = reverse("admin:auth_user_change", args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', user_admin_url, obj.user.username)
        return _('Anonymous')

    @admin.display(description=_('Game'), ordering='game__title')
    def game_display(self, obj):
        if obj.game:
            game_admin_url = reverse("admin:ratings_game_change", args=[obj.game.pk])
            return format_html('<a href="{}">{}</a>', game_admin_url, obj.game.title)
        return '-'

    @admin.display(description=_('Descriptor'), ordering='existing_descriptor__description')
    def descriptor_display(self, obj):
        if obj.existing_descriptor:
            return obj.existing_descriptor.description
        elif obj.suggested_descriptor_name:
            return f"({_('New')}) {obj.suggested_descriptor_name}"
        return '-'

    @admin.action(description=_('Mark selected suggestions as Approved'))
    def mark_approved(self, request, queryset):
        updated = queryset.update(status='APPROVED')
        self.message_user(request, _('%(count)d suggestions marked as Approved.') % {'count': updated}, messages.SUCCESS)

    @admin.action(description=_('Mark selected suggestions as Implemented'))
    def mark_implemented(self, request, queryset):
        updated = queryset.update(status='IMPLEMENTED')
        self.message_user(request, _('%(count)d suggestions marked as Implemented.') % {'count': updated}, messages.SUCCESS)

    @admin.action(description=_('Mark selected suggestions as Rejected'))
    def mark_rejected(self, request, queryset):
        updated = queryset.update(status='REJECTED')
        self.message_user(request, _('%(count)d suggestions marked as Rejected.') % {'count': updated}, messages.SUCCESS)

    @admin.action(description=_('Mark selected suggestions as Pending Review'))
    def mark_pending(self, request, queryset):
        updated = queryset.update(status='PENDING')
        self.message_user(request, _('%(count)d suggestions marked as Pending Review.') % {'count': updated}, messages.SUCCESS)


# --- MethodologyPageAdmin & WhyMGCPageAdmin ---
@admin.register(MethodologyPage)
class MethodologyPageAdmin(TranslationAdmin):
    list_display = ('title', 'last_updated')
    fields = ('title', 'content')
@admin.register(WhyMGCPage)
class WhyMGCPageAdmin(TranslationAdmin):
    list_display = ('title', 'last_updated')
    fields = ('title', 'content')

# --- BoycottedEntity Admin ---
@admin.register(BoycottedEntity)
class BoycottedEntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'entity_type', 'is_active', 'updated_date')
    list_filter = ('entity_type', 'is_active')
    search_fields = ('name', 'reason')
    prepopulated_fields = {'slug': ('name', 'entity_type')}
    list_editable = ('is_active',)
    actions = ['activate_boycotts', 'deactivate_boycotts']
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'entity_type', 'is_active')}),
        (_('Details'), {'fields': ('reason',)}),
        (_('Timestamps'), {'fields': ('created_date', 'updated_date'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_date', 'updated_date')

    @admin.action(description=_('Activate selected boycotts'))
    def activate_boycotts(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _('%(count)d boycott entries activated.') % {'count': updated}, messages.SUCCESS)

    @admin.action(description=_('Deactivate selected boycotts'))
    def deactivate_boycotts(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _('%(count)d boycott entries deactivated.') % {'count': updated}, messages.SUCCESS)