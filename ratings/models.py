# ratings/models.py - FULL FILE (with i18n)
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone # Needed if you add date/time fields later
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _ # Import for translation

# Represents the overall rating category (Halal, Mashbouh, etc.)
class RatingTier(models.Model):
    # --- MODIFY TIER_CHOICES display names ---
    TIER_CHOICES = [
        ('HAL', _('Halal')),      # Use simple name
        ('MSH', _('Mashbouh')),   # Use simple name
        ('HRM', _('Haram')),      # Use simple name
        ('KFR', _('Kufr')),       # Use simple name (Assuming KFR code for Kufr)
    ]
    tier_code = models.CharField(max_length=3, choices=TIER_CHOICES, unique=True, primary_key=True)
    # Use _() for verbose_name and help_text
    display_name = models.CharField(max_length=50, unique=True, verbose_name=_('Display Name'))
    icon_name = models.CharField(
        max_length=50,
        default="help",
        help_text=_("Material Symbols icon name (e.g., check_circle, warning, cancel, gpp_bad). See fonts.google.com/icons"),
        verbose_name=_('Icon Name')
    )
    color_hex = models.CharField(max_length=7, help_text=_("Hex color code, e.g., #00FF00"), verbose_name=_('Color Hex'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    order = models.PositiveIntegerField(default=0, help_text=_("Order to display tiers (0=first)"), verbose_name=_('Display Order'))

    class Meta:
        ordering = ['order']
        verbose_name = _('Rating Tier')
        verbose_name_plural = _('Rating Tiers')

    def __str__(self):
        # Return the display_name which is already marked for translation potentially
        # Or directly translate if needed, but display_name is usually sufficient
        return self.display_name # Keep as is, relies on display_name field

# Represents quick visual flags for content types
class Flag(models.Model):
    symbol = models.CharField(max_length=50, unique=True, verbose_name=_('Symbol (Icon Name)')) # Stores Material Symbol name
    description = models.CharField(max_length=100, verbose_name=_('Description'))

    class Meta:
        verbose_name = _('Content Flag')
        verbose_name_plural = _('Content Flags')

    def __str__(self):
        # F-strings can be tricky with lazy translation. Construct carefully if needed.
        # This is mostly for admin, so direct translation might not be critical here.
        return f"{self.symbol} - {self.description}"

# --- Critic Review Model ---
class CriticReview(models.Model):
    reviewer_name = models.CharField(max_length=100, help_text=_("e.g., IGN, GameSpot, Metacritic"), verbose_name=_('Reviewer Name'))
    score = models.CharField(max_length=20, blank=True, help_text=_("e.g., 9/10, 85/100, Recommended"), verbose_name=_('Score'))
    review_url = models.URLField(max_length=300, unique=True, help_text=_("Direct link to the review"), verbose_name=_('Review URL'))
    summary = models.TextField(blank=True, help_text=_("Optional short quote or summary from the review"), verbose_name=_('Summary Quote'))
    date_added = models.DateTimeField(auto_now_add=True, verbose_name=_('Date Added'))

    class Meta:
        ordering = ['reviewer_name']
        verbose_name = _('Critic Review')
        verbose_name_plural = _('Critic Reviews')

    def __str__(self):
        # Use translated placeholder if score is blank
        return f"{self.reviewer_name} ({self.score or _('No Score')})"

# Represents a specific video game and its detailed rating
class Game(models.Model):
    # --- Core Game Information ---
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    slug = models.SlugField(max_length=220, unique=True, blank=True, help_text=_("Unique URL-friendly name. Leave blank to auto-generate from title."))
    cover_image_url = models.URLField(max_length=300, blank=True, null=True, help_text=_("URL for the game's cover image."), verbose_name=_('Cover Image URL'))
    developer = models.CharField(max_length=100, blank=True, verbose_name=_('Developer'))
    publisher = models.CharField(max_length=100, blank=True, verbose_name=_('Publisher'))
    release_date = models.DateField(blank=True, null=True, verbose_name=_('Release Date'))
    summary = models.TextField(blank=True, help_text=_("Short description shown in lists."), verbose_name=_('Summary'))
    developer_slug = models.SlugField(max_length=110, blank=True, help_text=_("Auto-generated slug for developer filtering."))
    publisher_slug = models.SlugField(max_length=110, blank=True, help_text=_("Auto-generated slug for publisher filtering."))

    steam_link = models.URLField(_("Steam Store URL"), max_length=300, blank=True, null=True)
    epic_link = models.URLField(_("Epic Games Store URL"), max_length=300, blank=True, null=True)
    gog_link = models.URLField(_("GOG Store URL"), max_length=300, blank=True, null=True)
    other_store_link = models.URLField(_("Other Store URL"), max_length=300, blank=True, null=True)

    # --- START: Platform Availability Fields ---
    available_pc = models.BooleanField(_("Available on PC"), default=False)
    available_ps5 = models.BooleanField(_("Available on PS5"), default=False)
    available_ps4 = models.BooleanField(_("Available on PS4"), default=False)
    available_xbox_series = models.BooleanField(_("Available on Xbox Series X|S"), default=False)
    available_xbox_one = models.BooleanField(_("Available on Xbox One"), default=False)
    available_switch = models.BooleanField(_("Available on Nintendo Switch"), default=False)
    available_android = models.BooleanField(_("Available on Android"), default=False)
    available_ios = models.BooleanField(_("Available on iOS"), default=False)


    # --- MGC Rating & Flags ---
    rating_tier = models.ForeignKey(
        RatingTier, on_delete=models.PROTECT, related_name='games',
        help_text=_("Overall MGC Rating based on detailed assessment."), verbose_name=_('Rating Tier')
    )
    requires_adjustment = models.BooleanField(
        default=False, help_text=_("Check if this game needs user adjustments (settings, mods) to meet its assigned Halal/Mubah rating."),
        verbose_name=_('Requires Adjustment')
    )
    flags = models.ManyToManyField(
        Flag, blank=True, related_name='games',
        help_text=_("Quick visual indicators for potential content types."), verbose_name=_('Content Flags')
    )
    rationale = models.TextField(blank=True, help_text=_("General rationale summary (optional)."), verbose_name=_('General Rationale'))

    # --- Adjustment Guide ---
    adjustment_guide = models.TextField(
        blank=True, help_text=_("Instructions or links on how to adjust settings/mods for Halal/Mashbouh games."),
        verbose_name=_('Adjustment Guide')
    )

    # --- Detailed MGC Breakdown Fields ---
    SEVERITY_CHOICES = [
        # Use _() for display names
        ('N', _('None')), ('L', _('Low')), ('M', _('Medium')), ('H', _('High')), ('P', _('Prohibited')),
    ]
    # Wrap verbose_name, choices, help_text
    aqidah_severity = models.CharField(_('Aqidah Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    aqidah_details = models.TextField(_('Aqidah Details'), blank=True, help_text=_("Specific examples related to Aqidah concerns (magic, deities, ideologies etc)."))
    aqidah_reason = models.TextField(_('Aqidah Reason'), blank=True, help_text=_("Reasoning or reference for the Aqidah severity rating."))
    violence_severity = models.CharField(_('Violence Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    violence_details = models.TextField(_('Violence Details'), blank=True, help_text=_("Specific examples of violence, gore, context."))
    violence_reason = models.TextField(_('Violence Reason'), blank=True, help_text=_("Reasoning or reference for the Violence severity rating."))
    immorality_severity = models.CharField(_('Immorality Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    immorality_details = models.TextField(_('Immorality Details'), blank=True, help_text=_("Examples of 'Awrah, suggestive themes, promotion of impermissible relationships, bad language/conduct."))
    immorality_reason = models.TextField(_('Immorality Reason'), blank=True, help_text=_("Reasoning or reference for the Immorality severity rating."))
    substances_gambling_severity = models.CharField(_('Substances/Gambling Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    substances_gambling_details = models.TextField(_('Substances/Gambling Details'), blank=True, help_text=_("Examples of substance use/promotion, gambling mechanics."))
    substances_gambling_reason = models.TextField(_('Substances/Gambling Reason'), blank=True, help_text=_("Reasoning or reference for the Substances/Gambling severity rating."))
    audio_music_severity = models.CharField(_('Audio/Music Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    audio_music_details = models.TextField(_('Audio/Music Details'), blank=True, help_text=_("Details about background music, lyrics, ability to mute."))
    audio_music_reason = models.TextField(_('Audio/Music Reason'), blank=True, help_text=_("Reasoning or reference for the Audio/Music severity rating."))
    time_addiction_severity = models.CharField(_('Time/Addiction Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    time_addiction_details = models.TextField(_('Time/Addiction Details'), blank=True, help_text=_("Notes on addictive mechanics, time investment required, potential for neglecting duties."))
    time_addiction_reason = models.TextField(_('Time/Addiction Reason'), blank=True, help_text=_("Reasoning or reference for the Time/Addiction severity rating."))
    online_conduct_severity = models.CharField(_('Online Conduct Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    online_conduct_details = models.TextField(_('Online Conduct Details'), blank=True, help_text=_("Risks related to online chat, community toxicity, moderation."))
    online_conduct_reason = models.TextField(_('Online Conduct Reason'), blank=True, help_text=_("Reasoning or reference for the Online Conduct severity rating."))

    # --- Spoiler Flag ---
    has_spoilers_in_details = models.BooleanField(
        default=False, help_text=_("Check this to enable the 'Show/Hide Details' toggle for categories containing potential spoilers."),
        verbose_name=_('Has Spoilers in Details')
    )

    # --- Store Links ---
    steam_link = models.URLField(_("Steam Store URL"), max_length=300, blank=True, null=True)
    epic_link = models.URLField(_("Epic Games Store URL"), max_length=300, blank=True, null=True)
    gog_link = models.URLField(_("GOG Store URL"), max_length=300, blank=True, null=True)
    other_store_link = models.URLField(_("Other Store URL"), max_length=300, blank=True, null=True)

    # --- Relation to Critic Reviews ---
    critic_reviews = models.ManyToManyField(
        CriticReview,
        blank=True,
        related_name='games',
        help_text=_("Select critic reviews relevant to this game."),
        verbose_name=_('Critic Reviews')
    )

    # --- Timestamps ---
    date_added = models.DateTimeField(auto_now_add=True, verbose_name=_('Date Added')) # Added verbose_name
    date_updated = models.DateTimeField(auto_now=True, verbose_name=_('Date Updated')) # Added verbose_name

    class Meta:
        ordering = ['-date_added']
        verbose_name = _('Game')
        verbose_name_plural = _('Games')

    def save(self, *args, **kwargs):
        # Logic doesn't involve user-facing strings, no changes needed
        if not self.slug: self.slug = slugify(self.title)
        if self.developer and not self.developer_slug: self.developer_slug = slugify(self.developer)
        if self.publisher and not self.publisher_slug: self.publisher_slug = slugify(self.publisher)
        orMGCnal_slug = self.slug; counter = 1
        while Game.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f'{orMGCnal_slug}-{counter}'; counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('ratings:game_detail', kwargs={'game_slug': self.slug})

    def __str__(self):
        return self.title

    # --- Properties for template use ---
    # These rely on SEVERITY_CHOICES which are marked for translation
    @cached_property
    def aqidah_severity_display(self): return dict(self.SEVERITY_CHOICES).get(self.aqidah_severity, '?')
    @cached_property
    def aqidah_severity_css_class(self): return f"severity-{self.aqidah_severity}"
    @cached_property
    def violence_severity_display(self): return dict(self.SEVERITY_CHOICES).get(self.violence_severity, '?')
    @cached_property
    def violence_severity_css_class(self): return f"severity-{self.violence_severity}"
    @cached_property
    def immorality_severity_display(self): return dict(self.SEVERITY_CHOICES).get(self.immorality_severity, '?')
    @cached_property
    def immorality_severity_css_class(self): return f"severity-{self.immorality_severity}"
    @cached_property
    def substances_gambling_severity_display(self): return dict(self.SEVERITY_CHOICES).get(self.substances_gambling_severity, '?')
    @cached_property
    def substances_gambling_severity_css_class(self): return f"severity-{self.substances_gambling_severity}"
    @cached_property
    def audio_music_severity_display(self): return dict(self.SEVERITY_CHOICES).get(self.audio_music_severity, '?')
    @cached_property
    def audio_music_severity_css_class(self): return f"severity-{self.audio_music_severity}"
    @cached_property
    def time_addiction_severity_display(self): return dict(self.SEVERITY_CHOICES).get(self.time_addiction_severity, '?')
    @cached_property
    def time_addiction_severity_css_class(self): return f"severity-{self.time_addiction_severity}"
    @cached_property
    def online_conduct_severity_display(self): return dict(self.SEVERITY_CHOICES).get(self.online_conduct_severity, '?')
    @cached_property
    def online_conduct_severity_css_class(self): return f"severity-{self.online_conduct_severity}"