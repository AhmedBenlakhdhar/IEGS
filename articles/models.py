# articles/models.py
from django.db import models
from django.contrib.auth.models import User # Optional: Link to users later
from django.utils.text import slugify
from django.urls import reverse # Ensure reverse is imported
from django.utils import timezone

class Article(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=270, unique=True, blank=True, help_text="Unique URL-friendly name. Leave blank to auto-generate from title.")
    content = models.TextField()
    # author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # Optional
    author_name = models.CharField(max_length=100, blank=True, help_text="Display author name (if not linked to user)")
    published_date = models.DateTimeField(default=timezone.now, help_text="Set a future date to schedule publication.")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_date']
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this article."""
        # Corrected line using the 'articles' namespace
        return reverse('articles:article_detail', kwargs={'article_slug': self.slug})

    def save(self, *args, **kwargs):
        """ Auto-generates slug if blank and ensures uniqueness. """
        if not self.slug:
            self.slug = slugify(self.title)
         # Ensure slug is unique if auto-generated or manually changed
        original_slug = self.slug
        counter = 1
        queryset = Article.objects.filter(slug=self.slug)
        # Exclude self during check only if instance already has a primary key (is being updated)
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)

        while queryset.exists():
            self.slug = f'{original_slug}-{counter}'
            counter += 1
             # Re-filter based on the new potential slug
            queryset = Article.objects.filter(slug=self.slug)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title