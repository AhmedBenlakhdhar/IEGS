# articles/admin.py
from django.contrib import admin, messages
from modeltranslation.admin import TranslationAdmin
from .models import Article, ArticleCategory, ArticleCategoryMembership, ArticleComment
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth.models import User

@admin.register(ArticleCategory)
class ArticleCategoryAdmin(TranslationAdmin):
    list_display = ('name', 'slug', 'description')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    # No changes needed here

# Define Inline Admin for the through model
class ArticleCategoryMembershipInline(admin.TabularInline):
    model = ArticleCategoryMembership
    extra = 1
    autocomplete_fields = ['articlecategory'] # Improve UI for selecting categories

@admin.register(Article)
class ArticleAdmin(TranslationAdmin):
    list_display = ('title', 'author_name', 'published_date', 'updated_date')
    search_fields = ('title', 'content', 'author_name') # Searching translated fields might need care
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    ordering = ('-published_date',)
    fields = ('title', 'slug', 'header_image_url', 'author_name', 'published_date', 'content')
    list_filter = ('published_date', 'categories') # Can filter by category now via the M2M
    inlines = [ArticleCategoryMembershipInline]
    readonly_fields = ('created_date', 'updated_date') # Add auto-updated fields

@admin.register(ArticleComment)
class ArticleCommentAdmin(admin.ModelAdmin): # Not inheriting from TranslationAdmin
    list_display = ('article_link', 'user_link', 'created_date', 'approved', 'moderator_attention_needed', 'flag_count_display', 'content_preview')
    list_filter = ('approved', 'moderator_attention_needed', 'created_date', 'article')
    search_fields = ('content', 'user__username', 'article__title')
    actions = ['approve_comments', 'unapprove_comments', 'mark_reviewed', 'deactivate_commenter', 'reactivate_commenter']
    # Make user, article, created_date, and flagged_by readonly in the admin form
    readonly_fields = ('user', 'article', 'created_date', 'flagged_by', 'flag_count_display') # Add flag_count_display
    list_display_links = ('content_preview',) # Link from preview

    fieldsets = (
        (None, {'fields': ('article', 'user', 'created_date')}),
        (_('Content & Status'), {'fields': ('content', 'approved', 'moderator_attention_needed', 'flagged_by', 'flag_count_display')}), # Added flag_count_display here too
    )

    # Keep existing methods and actions as they are correct
    @admin.display(description=_('Article'), ordering='article__title')
    def article_link(self, obj):
        article_admin_url = reverse("admin:articles_article_change", args=[obj.article.pk])
        return format_html('<a href="{}">{}</a>', article_admin_url, obj.article.title)

    @admin.display(description=_('User'), ordering='user__username')
    def user_link(self, obj):
        user_admin_url = reverse("admin:auth_user_change", args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', user_admin_url, obj.user.username)

    @admin.display(description=_('Comment Preview'))
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    @admin.display(description=_('Flags'))
    def flag_count_display(self, obj):
        return obj.flag_count # Use the property

    @admin.action(description=_('Approve selected comments'))
    def approve_comments(self, request, queryset):
        updated = queryset.update(approved=True)
        self.message_user(request, _('%(updated)d comments were successfully approved.') % {'updated': updated}, messages.SUCCESS)

    @admin.action(description=_('Unapprove selected comments'))
    def unapprove_comments(self, request, queryset):
        updated = queryset.update(approved=False)
        self.message_user(request, _('%(updated)d comments were successfully unapproved.') % {'updated': updated}, messages.SUCCESS)

    @admin.action(description=_('Mark selected comments as reviewed (remove attention flag)'))
    def mark_reviewed(self, request, queryset):
        updated = queryset.update(moderator_attention_needed=False)
        self.message_user(request, _('%(updated)d comments marked as reviewed.') % {'updated': updated}, messages.SUCCESS)

    @admin.action(description=_('Deactivate (Ban) commenter accounts'))
    def deactivate_commenter(self, request, queryset):
        users_to_deactivate = User.objects.filter(pk__in=queryset.values_list('user__pk', flat=True))
        updated_count = users_to_deactivate.update(is_active=False)
        self.message_user(request, _('%(updated_count)d user accounts linked to selected comments were deactivated.') % {'updated_count': updated_count}, messages.SUCCESS)

    @admin.action(description=_('Reactivate commenter accounts'))
    def reactivate_commenter(self, request, queryset):
        users_to_reactivate = User.objects.filter(pk__in=queryset.values_list('user__pk', flat=True))
        updated_count = users_to_reactivate.update(is_active=True)
        self.message_user(request, _('%(updated_count)d user accounts linked to selected comments were reactivated.') % {'updated_count': updated_count}, messages.SUCCESS)