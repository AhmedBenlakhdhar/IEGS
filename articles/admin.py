# articles/admin.py
from django.contrib import admin, messages
# --- Import TranslationAdmin ---
from modeltranslation.admin import TranslationAdmin
from .models import Article, ArticleCategory, ArticleCategoryMembership, ArticleComment
from django.utils.translation import gettext_lazy as _
from django.urls import reverse # Import reverse
from django.utils.html import format_html # Import format_html
from django.contrib.auth.models import User # Import User

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

@admin.register(ArticleComment)
class ArticleCommentAdmin(admin.ModelAdmin): # Not inheriting from TranslationAdmin
    list_display = ('article_link', 'user_link', 'created_date', 'approved', 'moderator_attention_needed', 'flag_count_display', 'content_preview')
    list_filter = ('approved', 'moderator_attention_needed', 'created_date', 'article')
    search_fields = ('content', 'user__username', 'article__title')
    actions = ['approve_comments', 'unapprove_comments', 'mark_reviewed', 'deactivate_commenter', 'reactivate_commenter']
    readonly_fields = ('user', 'article', 'created_date', 'flagged_by') # Make flagged_by readonly
    list_display_links = ('content_preview',) # Link from preview

    fieldsets = (
        (None, {'fields': ('article', 'user', 'created_date')}),
        (_('Content & Status'), {'fields': ('content', 'approved', 'moderator_attention_needed', 'flagged_by')}),
    )

    def article_link(self, obj):
        # Link to the article in the admin
        article_admin_url = reverse("admin:articles_article_change", args=[obj.article.pk])
        return format_html('<a href="{}">{}</a>', article_admin_url, obj.article.title)
    article_link.short_description = _('Article')
    article_link.admin_order_field = 'article'

    def user_link(self, obj):
        # Link to the user in the admin
        user_admin_url = reverse("admin:auth_user_change", args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', user_admin_url, obj.user.username)
    user_link.short_description = _('User')
    user_link.admin_order_field = 'user'

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = _('Comment Preview')

    def flag_count_display(self, obj):
        return obj.flag_count # Use the property
    flag_count_display.short_description = _('Flags')
    # flag_count_display.admin_order_field = 'flag_count' # Requires annotation

    # --- Admin Actions (Similar to GameCommentAdmin) ---
    @admin.action(description=_('Approve selected comments'))
    def approve_comments(self, request, queryset):
        updated = queryset.update(approved=True)
        # Use blocktranslate for plurals
        self.message_user(request,
                          _('%(updated)d comments were successfully approved.') % {'updated': updated},
                          messages.SUCCESS)

    @admin.action(description=_('Unapprove selected comments'))
    def unapprove_comments(self, request, queryset):
        updated = queryset.update(approved=False)
        self.message_user(request,
                           _('%(updated)d comments were successfully unapproved.') % {'updated': updated},
                           messages.SUCCESS)

    @admin.action(description=_('Mark selected comments as reviewed (remove attention flag)'))
    def mark_reviewed(self, request, queryset):
        updated = queryset.update(moderator_attention_needed=False)
        self.message_user(request,
                           _('%(updated)d comments marked as reviewed.') % {'updated': updated},
                           messages.SUCCESS)

    @admin.action(description=_('Deactivate (Ban) commenter accounts'))
    def deactivate_commenter(self, request, queryset):
        users_to_deactivate = User.objects.filter(pk__in=queryset.values_list('user__pk', flat=True))
        updated_count = users_to_deactivate.update(is_active=False)
        self.message_user(request,
                           _('%(updated_count)d user accounts linked to selected comments were deactivated.') % {'updated_count': updated_count},
                           messages.SUCCESS)

    @admin.action(description=_('Reactivate commenter accounts'))
    def reactivate_commenter(self, request, queryset):
        users_to_reactivate = User.objects.filter(pk__in=queryset.values_list('user__pk', flat=True))
        updated_count = users_to_reactivate.update(is_active=True)
        self.message_user(request,
                           _('%(updated_count)d user accounts linked to selected comments were reactivated.') % {'updated_count': updated_count},
                           messages.SUCCESS)
# --- END: Article Comment Admin ---
