# articles/models.py (with i18n)
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _ # Import for translation

class Article(models.Model):
    # Use _() for verbose_name and help_text
    title = models.CharField(max_length=250, verbose_name=_('Title'))
    slug = models.SlugField(max_length=270, unique=True, blank=True, help_text=_("Unique URL-friendly name. Leave blank to auto-generate from title."))
    header_image_url = models.URLField(max_length=300, blank=True, null=True, help_text=_("URL for an image to display at the top of the article."), verbose_name=_('Header Image URL'))
    content = models.TextField(verbose_name=_('Content'))
    author_name = models.CharField(max_length=100, blank=True, help_text=_("Display author name (if not linked to user)"), verbose_name=_('Author Name'))
    published_date = models.DateTimeField(default=timezone.now, verbose_name=_('Published Date'))
    created_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Created Date'))
    updated_date = models.DateTimeField(auto_now=True, verbose_name=_('Updated Date'))

    class Meta:
        ordering = ['-published_date']
        # Use _() for verbose names
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