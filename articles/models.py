# articles/models.py (with i18n)
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User

# --- NEW: Article Category Model ---
class ArticleCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Category Name'))
    slug = models.SlugField(max_length=110, unique=True, blank=True, help_text=_("URL-friendly name, leave blank to auto-generate."))
    description = models.TextField(blank=True, verbose_name=_('Description'))

    class Meta:
        verbose_name = _("Article Category")
        verbose_name_plural = _("Article Categories")
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('articles:article_list_by_category', kwargs={'category_slug': self.slug})

    def __str__(self):
        return self.name
# ------------------------------------

class Article(models.Model):
    title = models.CharField(max_length=250, verbose_name=_('Title'))
    slug = models.SlugField(max_length=270, unique=True, blank=True, help_text=_("Unique URL-friendly name. Leave blank to auto-generate from title."))
    categories = models.ManyToManyField(
        ArticleCategory,
        through='ArticleCategoryMembership', # <--- DEFINE through model
        blank=True,
        related_name='articles',
        verbose_name=_('Categories')
    )
    header_image_url = models.URLField(max_length=300, blank=True, null=True, help_text=_("URL for an image to display at the top of the article."), verbose_name=_('Header Image URL'))
    content = RichTextUploadingField(verbose_name=_('Content'))
    author_name = models.CharField(max_length=100, blank=True, help_text=_("Display author name (if not linked to user)"), verbose_name=_('Author Name'))
    published_date = models.DateTimeField(default=timezone.now, verbose_name=_('Published Date'))
    created_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Created Date'))
    updated_date = models.DateTimeField(auto_now=True, verbose_name=_('Updated Date'))

    class Meta:
        ordering = ['-published_date']
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")


    def get_absolute_url(self):
        """Returns the URL to access a detail record for this article."""
        return reverse('articles:article_detail', kwargs={'article_slug': self.slug})

    def save(self, *args, **kwargs):
        """ Auto-generates slug if blank and ensures uniqueness. """
        # Logic doesn't involve user-facing strings, no changes needed
        if not self.slug:
            self.slug = slugify(self.title)
        original_slug = self.slug
        counter = 1
        queryset = Article.objects.filter(slug=self.slug)
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)

        while queryset.exists():
            self.slug = f'{original_slug}-{counter}'
            counter += 1
            queryset = Article.objects.filter(slug=self.slug)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

# --- DEFINE the explicit intermediate model ---
class ArticleCategoryMembership(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    # Ensure the ForeignKey name matches the model name (lowercase)
    articlecategory = models.ForeignKey(ArticleCategory, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('article', 'articlecategory') # Prevent duplicates
        # Optional: Define verbose names if needed for admin
        # verbose_name = _("Article Category Membership")
        # verbose_name_plural = _("Article Category Memberships")
# -------------------------------------------

# --- Article Comment Model ---
class ArticleComment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='article_comments')
    content = models.TextField(_('Comment'))
    created_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Date Posted'))
    approved = models.BooleanField(default=True, verbose_name=_('Approved')) # Auto-approve comments
    flagged_by = models.ManyToManyField(User, related_name='flagged_article_comments', blank=True, verbose_name=_('Flagged By'))
    moderator_attention_needed = models.BooleanField(default=False, verbose_name=_('Needs Attention'))

    class Meta:
        ordering = ['created_date'] # Order oldest first for display
        verbose_name = _('Article Comment')
        verbose_name_plural = _('Article Comments')

    def __str__(self):
        status = _('Approved') if self.approved else _('Unapproved')
        if self.moderator_attention_needed:
            status += f" ({_('Flagged')})"
        # Use blocktranslate format specifiers for better translation context
        return _("Comment by %(username)s on Article '%(article_title)s' (%(status)s)") % {
            'username': self.user.username,
            'article_title': self.article.title,
            'status': status
        }

    @property
    def flag_count(self):
        """Returns the number of users who flagged this comment."""
        return self.flagged_by.count()
# --- END: Article Comment Model ---