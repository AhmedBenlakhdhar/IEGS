# ratings/models.py
from django.db import models
from django.utils.text import slugify
from django.urls import reverse # Ensure reverse is imported
from django.utils import timezone # If needed for date fields

class RatingTier(models.Model):
    TIER_CHOICES = [
        ('HAL', '✅ Halal / Mubah'),
        ('MSH', '⚠️ Mashbouh'),
        ('HRM', '❌ Haram'),
        ('KSK', '🛑 Kufr / Shirk'),
    ]
    # Use a short code for internal reference, ensure it's unique
    tier_code = models.CharField(max_length=3, choices=TIER_CHOICES, unique=True, primary_key=True)
    # Store the full display name including symbol
    display_name = models.CharField(max_length=50, unique=True)
    color_hex = models.CharField(max_length=7, help_text="Hex color code, e.g., #00FF00")
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Order to display tiers (0=first)")

    class Meta:
        ordering = ['order']
        verbose_name = "Rating Tier"
        verbose_name_plural = "Rating Tiers"

    def __str__(self):
        return self.display_name

class Flag(models.Model):
    symbol = models.CharField(max_length=5, unique=True)
    description = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Content Flag"
        verbose_name_plural = "Content Flags"

    def __str__(self):
        return f"{self.symbol} - {self.description}"

class Game(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True, help_text="Unique URL-friendly name. Leave blank to auto-generate from title.")
    summary = models.TextField(blank=True, help_text="Short description shown in lists.")
    # For simplicity initially, use a URL. Later you could use ImageField
    cover_image_url = models.URLField(max_length=300, blank=True, null=True, help_text="URL for the game's cover image.")
    rating_tier = models.ForeignKey(RatingTier, on_delete=models.PROTECT, related_name='games', verbose_name="Rating Tier")
    rationale = models.TextField(help_text="Detailed justification for the rating.")
    flags = models.ManyToManyField(Flag, blank=True, related_name='games', verbose_name="Content Flags")
    developer = models.CharField(max_length=100, blank=True)
    publisher = models.CharField(max_length=100, blank=True)
    release_date = models.DateField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_added'] # Show newest games first
        verbose_name = "Game Rating"
        verbose_name_plural = "Game Ratings"

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this game."""
        # Corrected line using the 'ratings' namespace
        return reverse('ratings:game_detail', kwargs={'game_slug': self.slug})

    def save(self, *args, **kwargs):
        """ Auto-generates slug if blank and ensures uniqueness. """
        if not self.slug:
            self.slug = slugify(self.title)
        # Ensure slug is unique if auto-generated or manually changed
        original_slug = self.slug
        counter = 1
        queryset = Game.objects.filter(slug=self.slug)
        # Exclude self during check only if instance already has a primary key (is being updated)
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)

        while queryset.exists():
            self.slug = f'{original_slug}-{counter}'
            counter += 1
            # Re-filter based on the new potential slug
            queryset = Game.objects.filter(slug=self.slug)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title