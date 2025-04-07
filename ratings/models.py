# ratings/models.py
# (No structural changes needed from the version AFTER adding original_rating_tier)
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField

# Represents the overall rating category (Halal, Mashbouh, etc.)
class RatingTier(models.Model):
    TIER_CHOICES = [
        ('HAL', _('Halal')),
        ('MSH', _('Mashbouh')),
        ('HRM', _('Haram')),
        ('KFR', _('Kufr')),
    ]
    tier_code = models.CharField(max_length=3, choices=TIER_CHOICES, unique=True, primary_key=True)
    display_name = models.CharField(max_length=50, unique=True, verbose_name=_('Display Name'))
    icon_name = models.CharField(max_length=50, default="help", help_text=_("Material Symbols icon name (e.g., check_circle, warning, cancel, gpp_bad). See fonts.google.com/icons"), verbose_name=_('Icon Name'))
    color_hex = models.CharField(max_length=7, help_text=_("Hex color code, e.g., #00FF00"), verbose_name=_('Color Hex'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    order = models.PositiveIntegerField(default=0, help_text=_("Order to display tiers (0=first)"), verbose_name=_('Display Order'))

    class Meta:
        ordering = ['order']
        verbose_name = _('Rating Tier')
        verbose_name_plural = _('Rating Tiers')

    def __str__(self):
        return self.display_name

# Represents quick visual flags for content types
class Flag(models.Model):
    symbol = models.CharField(max_length=50, unique=True, verbose_name=_('Symbol (Icon Name)'))
    description = models.CharField(max_length=100, verbose_name=_('Description'))

    class Meta:
        verbose_name = _('Content Flag')
        verbose_name_plural = _('Content Flags')

    def __str__(self):
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

    # --- Platform Availability Fields ---
    available_pc = models.BooleanField(_("Available on PC"), default=False)
    available_ps5 = models.BooleanField(_("Available on PS5"), default=False)
    available_ps4 = models.BooleanField(_("Available on PS4"), default=False)
    available_xbox_series = models.BooleanField(_("Available on Xbox Series X|S"), default=False)
    available_xbox_one = models.BooleanField(_("Available on Xbox One"), default=False)
    available_switch = models.BooleanField(_("Available on Nintendo Switch"), default=False)
    available_android = models.BooleanField(_("Available on Android"), default=False)
    available_ios = models.BooleanField(_("Available on iOS"), default=False)
    available_quest = models.BooleanField(_("Available on Meta Quest"), default=False)

    # --- MGC Rating & Flags ---
    # **IMPORTANT**: rating_tier now always stores the FINAL/ACHIEVABLE tier after potential adjustments.
    rating_tier = models.ForeignKey(
        RatingTier,
        on_delete=models.PROTECT,
        related_name='games_final_tier',
        help_text=_("Overall MGC Rating based on detailed assessment (AFTER adjustment, if any)."),
        verbose_name=_('Rating Tier (Final/Achievable)') # Clarified verbose name
    )
    # **IMPORTANT**: original_rating_tier stores the tier BEFORE adjustments, ONLY IF requires_adjustment is True.
    original_rating_tier = models.ForeignKey(
        RatingTier,
        on_delete=models.SET_NULL,
        related_name='games_originally_this_tier',
        null=True, blank=True,
        verbose_name=_('Original Rating Tier (Before Adjustment)'),
        help_text=_("The game's rating before required adjustments were applied. Only set if 'Requires Adjustment' is True.")
    )
    requires_adjustment = models.BooleanField(
        default=False, help_text=_("Check if this game needs user adjustments (settings, mods) to meet its assigned final rating tier."),
        verbose_name=_('Requires Adjustment')
    )
    flags = models.ManyToManyField(
        Flag,
        blank=True,
        related_name='games_with_flag',
        help_text=_("Quick visual indicators for potential content types."),
        verbose_name=_('Content Flags')
    )
    adjustable_flags = models.ManyToManyField(
        Flag,
        blank=True,
        related_name='games_needing_adjustment',
        help_text=_("Select flags corresponding to content that CAN be adjusted/avoided."),
        verbose_name=_('Adjustable Content Flags')
    )
    rationale = models.TextField(blank=True, help_text=_("General rationale summary (optional)."), verbose_name=_('General Rationale'))
    adjustment_guide = models.TextField(
        blank=True, help_text=_("Instructions or links on how to adjust settings/mods for Halal/Mashbouh games."),
        verbose_name=_('Adjustment Guide')
    )

    # --- Detailed MGC Breakdown Fields ---
    SEVERITY_CHOICES = [
        ('N', _('None')), ('L', _('Low')), ('M', _('Medium')), ('H', _('High')), ('P', _('Prohibited')),
    ]
    aqidah_severity = models.CharField(_('Aqidah Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    aqidah_details = models.TextField(_('Aqidah Details'), blank=True, help_text=_("Specific examples related to Aqidah concerns (magic, deities, ideologies etc)."))
    aqidah_reason = models.TextField(_('Aqidah Reason'), blank=True, help_text=_("Reasoning or reference for the Aqidah severity rating."))
    haram_depictions_severity = models.CharField(_('Haram Depictions Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    haram_depictions_details = models.TextField(_('Haram Depictions Details'), blank=True, help_text=_("Examples: Required exposure to 'Awrah, Haram music, gambling mechanics, etc."))
    haram_depictions_reason = models.TextField(_('Haram Depictions Reason'), blank=True, help_text=_("Reasoning for the Depictions severity rating."))
    simulation_haram_severity = models.CharField(_('Simulation Haram Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    simulation_haram_details = models.TextField(_('Simulation Haram Details'), blank=True, help_text=_("Examples: Simulating drinking Khamr, simulated Zina, performing simulated Shirk acts."))
    simulation_haram_reason = models.TextField(_('Simulation Haram Reason'), blank=True, help_text=_("Reasoning for the Simulation Haram severity rating."))
    normalization_haram_severity = models.CharField(_('Normalization Haram Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    normalization_haram_details = models.TextField(_('Normalization Haram Details'), blank=True, help_text=_("Examples: Positive portrayal of impermissible relationships, casual depiction of sin, trivialization."))
    normalization_haram_reason = models.TextField(_('Normalization Haram Reason'), blank=True, help_text=_("Reasoning for the Normalization Haram severity rating."))
    violence_severity = models.CharField(_('Violence Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    violence_details = models.TextField(_('Violence Details'), blank=True, help_text=_("Specific examples of violence, gore, context, justification."))
    violence_reason = models.TextField(_('Violence Reason'), blank=True, help_text=_("Reasoning for the Violence severity rating."))
    time_addiction_severity = models.CharField(_('Time/Addiction Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    time_addiction_details = models.TextField(_('Time/Addiction Details'), blank=True, help_text=_("Notes on addictive mechanics, time investment required, potential for neglecting duties."))
    time_addiction_reason = models.TextField(_('Time/Addiction Reason'), blank=True, help_text=_("Reasoning for the Time/Addiction severity rating."))
    online_conduct_severity = models.CharField(_('Online Conduct Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    online_conduct_details = models.TextField(_('Online Conduct Details'), blank=True, help_text=_("Risks related to online chat, community toxicity, moderation."))
    online_conduct_reason = models.TextField(_('Online Conduct Reason'), blank=True, help_text=_("Reasoning for the Online Conduct severity rating."))

    # --- Spoiler Flag ---
    has_spoilers_in_details = models.BooleanField( default=False, help_text=_("Check this to enable the 'Show/Hide Details' toggle for categories containing potential spoilers."), verbose_name=_('Has Spoilers in Details'))

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
    date_added = models.DateTimeField(auto_now_add=True, verbose_name=_('Date Added'))
    date_updated = models.DateTimeField(auto_now=True, verbose_name=_('Date Updated'))

    class Meta:
        ordering = ['-date_added']
        verbose_name = _('Game')
        verbose_name_plural = _('Games')

    def save(self, *args, **kwargs):
        # Auto-generate slugs if blank
        if not self.slug: self.slug = slugify(self.title)
        if self.developer and not self.developer_slug: self.developer_slug = slugify(self.developer)
        if self.publisher and not self.publisher_slug: self.publisher_slug = slugify(self.publisher)

        # Ensure slug uniqueness if needed (add counter if duplicate)
        original_slug = self.slug
        counter = 1
        queryset = Game.objects.filter(slug=self.slug)
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)
        while queryset.exists():
            self.slug = f'{original_slug}-{counter}'
            counter += 1
            # Re-query with the new slug attempt
            queryset = Game.objects.filter(slug=self.slug)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)

        # Ensure original_rating_tier is cleared if requires_adjustment is False
        if not self.requires_adjustment:
            self.original_rating_tier = None

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('ratings:game_detail', kwargs={'game_slug': self.slug})

    def __str__(self):
        return self.title

    # --- Cached Properties for Severity (no changes needed) ---
    @cached_property
    def aqidah_severity_display(self): return dict(self.SEVERITY_CHOICES).get(self.aqidah_severity, '?')
    # ... (other severity display properties remain the same) ...
    @cached_property
    def online_conduct_severity_css_class(self): return f"severity-{self.online_conduct_severity}"

# --- GameComment Model ---
# ... (No changes needed) ...
class GameComment(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_comments')
    content = models.TextField(_('Comment'))
    created_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Date Posted'))
    approved = models.BooleanField(default=True, verbose_name=_('Approved'))
    flagged_by = models.ManyToManyField(User, related_name='flagged_comments', blank=True, verbose_name=_('Flagged By'))
    moderator_attention_needed = models.BooleanField(default=False, verbose_name=_('Needs Attention'))

    class Meta:
        ordering = ['created_date']
        verbose_name = _('Game Comment')
        verbose_name_plural = _('Game Comments')

    def __str__(self):
        status = _('Approved') if self.approved else _('Unapproved')
        if self.moderator_attention_needed:
            status += f" ({_('Flagged')})"
        return _("Comment by %(username)s on %(game_title)s (%(status)s)") % {
            'username': self.user.username,
            'game_title': self.game.title,
            'status': status
        }

    @property
    def flag_count(self):
        return self.flagged_by.count()

# --- MethodologyPage Model ---
# ... (No changes needed) ...
class MethodologyPage(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('Page Title'))
    content = RichTextUploadingField(verbose_name=_('Page Content'))
    last_updated = models.DateTimeField(auto_now=True, verbose_name=_('Last Updated'))

    class Meta:
        verbose_name = _("Methodology Page")
        verbose_name_plural = _("Methodology Page")

    def __str__(self):
        return self.title