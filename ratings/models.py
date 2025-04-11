# ratings/models.py
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property # Keep if needed elsewhere
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import IntegrityError

# --- RatingTier ---
class RatingTier(models.Model):
    tier_code = models.CharField(max_length=3, unique=True, primary_key=True)
    display_name = models.CharField(max_length=50, unique=True, verbose_name=_('Display Name'))
    icon_name = models.CharField(max_length=50, default="help", help_text=_("Material Symbols icon name"), verbose_name=_('Icon Name'))
    color_hex = models.CharField(max_length=7, help_text=_("Hex color code"), verbose_name=_('Color Hex'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    order = models.PositiveIntegerField(default=0, help_text=_("Display Order"), verbose_name=_('Display Order'))

    class Meta:
        ordering = ['order']
        verbose_name = _('Rating Tier')
        verbose_name_plural = _('Rating Tiers')

    def __str__(self):
        return str(self.display_name)

# --- Flag ---
class Flag(models.Model):
    symbol = models.CharField(max_length=100, unique=True, verbose_name=_('Symbol (Identifier)'))
    description = models.CharField(max_length=150, verbose_name=_('Description'))

    class Meta:
        verbose_name = _('Content Flag')
        verbose_name_plural = _('Content Flags')
        ordering = ['symbol']

    def __str__(self):
        return str(self.description)

# --- CriticReview ---
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

# --- Game ---
class Game(models.Model):
    # Core Info
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    slug = models.SlugField(max_length=220, unique=True, blank=True, help_text=_("Unique URL-friendly name. Leave blank to auto-generate from title."))
    cover_image_url = models.URLField(max_length=300, blank=True, null=True, help_text=_("URL for the game's cover image."), verbose_name=_('Cover Image URL'))
    developer = models.CharField(max_length=100, blank=True, verbose_name=_('Developer'))
    publisher = models.CharField(max_length=100, blank=True, verbose_name=_('Publisher'))
    release_date = models.DateField(blank=True, null=True, verbose_name=_('Release Date'))
    summary = models.TextField(blank=True, help_text=_("Short description shown in lists."), verbose_name=_('Summary'))
    developer_slug = models.SlugField(max_length=110, blank=True, help_text=_("Auto-generated slug for developer filtering."))
    publisher_slug = models.SlugField(max_length=110, blank=True, help_text=_("Auto-generated slug for publisher filtering."))

    # Platforms
    available_pc = models.BooleanField(_("Available on PC"), default=False)
    available_ps5 = models.BooleanField(_("Available on PS5"), default=False)
    available_ps4 = models.BooleanField(_("Available on PS4"), default=False)
    available_xbox_series = models.BooleanField(_("Available on Xbox Series X|S"), default=False)
    available_xbox_one = models.BooleanField(_("Available on Xbox One"), default=False)
    available_switch = models.BooleanField(_("Available on Nintendo Switch"), default=False)
    available_android = models.BooleanField(_("Available on Android"), default=False)
    available_ios = models.BooleanField(_("Available on iOS"), default=False)
    available_quest = models.BooleanField(_("Available on Meta Quest"), default=False)

    # Rating & Flags
    rating_tier = models.ForeignKey( RatingTier, on_delete=models.PROTECT, related_name='games_rated', help_text=_("Overall MGC Rating calculated based on detailed assessment."), verbose_name=_('Overall Rating Tier') )
    flags = models.ManyToManyField( Flag, blank=True, related_name='games_flagged', help_text=_("Flags automatically assigned based on detailed severity ratings."), verbose_name=_('Content Flags (Auto-assigned)') )
    rationale = models.TextField(blank=True, help_text=_("Overall reasoning summary for the final rating."), verbose_name=_('Rating Summary'))

    # Severity Choices
    SEVERITY_CHOICES = [
        ('N', _('None')),
        ('L', _('Mild')),
        ('M', _('Moderate')),
        ('S', _('Severe')),
    ]

    # --- Breakdown Severity Fields ONLY ---
    forced_shirk_severity = models.CharField(_('1. Forced Shirk Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    promote_shirk_severity = models.CharField(_('2. Promote Shirk/Kufr Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    insult_islam_severity = models.CharField(_('3. Insult Islam Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    depict_unseen_severity = models.CharField(_('4. Depict Unseen Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    magic_sorcery_severity = models.CharField(_('5. Magic/Sorcery Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    contradictory_ideologies_severity = models.CharField(_('6. Contradictory Ideologies Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    nudity_lewdness_severity = models.CharField(_('7. Nudity/Lewdness Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    music_instruments_severity = models.CharField(_('8. Music/Instruments Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    gambling_severity = models.CharField(_('9. Gambling/Maysir Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    lying_severity = models.CharField(_('10. Lying (Player) Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    simulate_killing_severity = models.CharField(_('11. Simulate Killing/Aggression Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    simulate_theft_crime_severity = models.CharField(_('12. Simulate Theft/Crime Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    normalize_haram_rels_severity = models.CharField(_('13. Normalize Haram Relationships Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    normalize_substances_severity = models.CharField(_('14. Normalize Substances Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    profanity_obscenity_severity = models.CharField(_('15. Profanity/Obscenity Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    time_wasting_severity = models.CharField(_('16. Excessive Time Wasting Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    financial_extravagance_severity = models.CharField(_('17. Financial Extravagance Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    online_communication_severity = models.CharField(_('18. Online Communication Risks Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    ugc_risks_severity = models.CharField(_('19. User Generated Content Risks Severity'), max_length=1, choices=SEVERITY_CHOICES, default='N')

    # Other Fields
    has_spoilers_in_details = models.BooleanField( default=False, help_text=_("Check this to enable the 'Show/Hide Details' toggle for categories containing potential spoilers."), verbose_name=_('Has Spoilers in Details'))
    steam_link = models.URLField(_("Steam Store URL"), max_length=300, blank=True, null=True)
    epic_link = models.URLField(_("Epic Games Store URL"), max_length=300, blank=True, null=True)
    gog_link = models.URLField(_("GOG Store URL"), max_length=300, blank=True, null=True)
    other_store_link = models.URLField(_("Other Store URL"), max_length=300, blank=True, null=True)
    critic_reviews = models.ManyToManyField( CriticReview, blank=True, related_name='games', help_text=_("Select critic reviews relevant to this game."), verbose_name=_('Critic Reviews') )
    date_added = models.DateTimeField(auto_now_add=True, verbose_name=_('Date Added'))
    date_updated = models.DateTimeField(auto_now=True, verbose_name=_('Date Updated'))

    # Class Attributes for Logic
    SEVERITY_FIELD_TO_FLAG_SYMBOL = { 'forced_shirk_severity': 'gpp_bad', 'promote_shirk_severity': 'hub', 'insult_islam_severity': 'report_problem', 'depict_unseen_severity': 'cloud_off', 'magic_sorcery_severity': 'auto_fix_high', 'contradictory_ideologies_severity': 'record_voice_over', 'nudity_lewdness_severity': 'visibility_off', 'music_instruments_severity': 'music_off', 'gambling_severity': 'casino', 'lying_severity': 'front_hand', 'simulate_killing_severity': 'swords', 'simulate_theft_crime_severity': 'local_police', 'normalize_haram_rels_severity': 'heart_broken', 'normalize_substances_severity': 'local_bar', 'profanity_obscenity_severity': 'speaker_notes_off', 'time_wasting_severity': 'hourglass_top', 'financial_extravagance_severity': 'monetization_on', 'online_communication_severity': 'forum', 'ugc_risks_severity': 'extension', }
    CATEGORY_FIELDS_IN_ORDER = [ 'forced_shirk', 'promote_shirk', 'insult_islam', 'depict_unseen', 'magic_sorcery', 'contradictory_ideologies', 'nudity_lewdness', 'music_instruments', 'gambling', 'lying', 'simulate_killing', 'simulate_theft_crime', 'normalize_haram_rels', 'normalize_substances', 'profanity_obscenity', 'time_wasting', 'financial_extravagance', 'online_communication', 'ugc_risks' ]

    class Meta:
        ordering = ['-date_added']
        verbose_name = _('Game')
        verbose_name_plural = _('Games')

    def calculate_global_rating_tier(self):
        try:
            tier_kfr = RatingTier.objects.get(tier_code='KFR')
            tier_hrm = RatingTier.objects.get(tier_code='HRM')
            tier_msh = RatingTier.objects.get(tier_code='MSH')
            tier_hal = RatingTier.objects.get(tier_code='HAL')
        except RatingTier.DoesNotExist:
            return RatingTier.objects.filter(tier_code='MSH').first() or None

        aqidah_severe_fields = [
            self.forced_shirk_severity, self.promote_shirk_severity,
            self.insult_islam_severity, self.magic_sorcery_severity
        ]
        if 'S' in aqidah_severe_fields:
            return tier_kfr

        non_aqidah_severe_triggers = [
            self.nudity_lewdness_severity, self.music_instruments_severity,
            self.gambling_severity, self.simulate_killing_severity,
            self.simulate_theft_crime_severity, self.normalize_haram_rels_severity,
            self.normalize_substances_severity, self.profanity_obscenity_severity,
            self.financial_extravagance_severity
        ]
        if 'S' in non_aqidah_severe_triggers:
            return tier_hrm

        all_severities = [ getattr(self, f + '_severity', 'N') for f in self.CATEGORY_FIELDS_IN_ORDER ]
        medium_count = all_severities.count('M')
        mild_count = all_severities.count('L')

        if medium_count >= 5:
            return tier_hrm
        if medium_count >= 1 or mild_count >= 3:
            return tier_msh

        return tier_hal

    def get_flags_based_on_severity(self):
        return [
            flag_symbol for field, flag_symbol in self.SEVERITY_FIELD_TO_FLAG_SYMBOL.items()
            if getattr(self, field, 'N') in ['L', 'M', 'S']
        ]

    def save(self, *args, **kwargs):
        # Slug generation
        if not self.slug:
            self.slug = slugify(self.title)
        if self.developer and not self.developer_slug:
            self.developer_slug = slugify(self.developer)
        if self.publisher and not self.publisher_slug:
            self.publisher_slug = slugify(self.publisher)

        # Ensure slug uniqueness if creating a new game
        if not self.pk:
            original_slug = self.slug
            counter = 1
            while Game.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1

        # Calculate and set rating tier BEFORE first save if possible
        if not hasattr(self, 'rating_tier') or not self.rating_tier_id: # Check if tier is not set or not saved yet
            calculated_tier = self.calculate_global_rating_tier()
            if calculated_tier:
                self.rating_tier = calculated_tier
            else: # Fallback if calculation fails
                try:
                    self.rating_tier = RatingTier.objects.get(tier_code='MSH')
                except RatingTier.DoesNotExist:
                    self.rating_tier = None # Or handle more robustly

        # Call the original save method
        super().save(*args, **kwargs)

        # Update M2M flags *after* saving and having a PK and a valid rating_tier
        if self.pk and self.rating_tier:
            try:
                flags_to_set = Flag.objects.filter(symbol__in=self.get_flags_based_on_severity())
                self.flags.set(flags_to_set)
            except Exception as e:
                # Handle potential errors during flag setting if needed
                print(f"Error setting flags for game {self.pk}: {e}")

    def get_absolute_url(self):
        return reverse('ratings:game_detail', kwargs={'game_slug': self.slug})

    def __str__(self):
        return self.title

    def get_severity_display_name(self, severity_code):
        return dict(self.SEVERITY_CHOICES).get(severity_code, '?')

    # --- Display & CSS Class Properties ---
    @property
    def forced_shirk_severity_display(self): return self.get_severity_display_name(self.forced_shirk_severity)
    @property
    def promote_shirk_severity_display(self): return self.get_severity_display_name(self.promote_shirk_severity)
    @property
    def insult_islam_severity_display(self): return self.get_severity_display_name(self.insult_islam_severity)
    @property
    def depict_unseen_severity_display(self): return self.get_severity_display_name(self.depict_unseen_severity)
    @property
    def magic_sorcery_severity_display(self): return self.get_severity_display_name(self.magic_sorcery_severity)
    @property
    def contradictory_ideologies_severity_display(self): return self.get_severity_display_name(self.contradictory_ideologies_severity)
    @property
    def nudity_lewdness_severity_display(self): return self.get_severity_display_name(self.nudity_lewdness_severity)
    @property
    def music_instruments_severity_display(self): return self.get_severity_display_name(self.music_instruments_severity)
    @property
    def gambling_severity_display(self): return self.get_severity_display_name(self.gambling_severity)
    @property
    def lying_severity_display(self): return self.get_severity_display_name(self.lying_severity)
    @property
    def simulate_killing_severity_display(self): return self.get_severity_display_name(self.simulate_killing_severity)
    @property
    def simulate_theft_crime_severity_display(self): return self.get_severity_display_name(self.simulate_theft_crime_severity)
    @property
    def normalize_haram_rels_severity_display(self): return self.get_severity_display_name(self.normalize_haram_rels_severity)
    @property
    def normalize_substances_severity_display(self): return self.get_severity_display_name(self.normalize_substances_severity)
    @property
    def profanity_obscenity_severity_display(self): return self.get_severity_display_name(self.profanity_obscenity_severity)
    @property
    def time_wasting_severity_display(self): return self.get_severity_display_name(self.time_wasting_severity)
    @property
    def financial_extravagance_severity_display(self): return self.get_severity_display_name(self.financial_extravagance_severity)
    @property
    def online_communication_severity_display(self): return self.get_severity_display_name(self.online_communication_severity)
    @property
    def ugc_risks_severity_display(self): return self.get_severity_display_name(self.ugc_risks_severity)
    @property
    def forced_shirk_severity_css_class(self): return f"severity-{self.forced_shirk_severity.lower()}"
    @property
    def promote_shirk_severity_css_class(self): return f"severity-{self.promote_shirk_severity.lower()}"
    @property
    def insult_islam_severity_css_class(self): return f"severity-{self.insult_islam_severity.lower()}"
    @property
    def depict_unseen_severity_css_class(self): return f"severity-{self.depict_unseen_severity.lower()}"
    @property
    def magic_sorcery_severity_css_class(self): return f"severity-{self.magic_sorcery_severity.lower()}"
    @property
    def contradictory_ideologies_severity_css_class(self): return f"severity-{self.contradictory_ideologies_severity.lower()}"
    @property
    def nudity_lewdness_severity_css_class(self): return f"severity-{self.nudity_lewdness_severity.lower()}"
    @property
    def music_instruments_severity_css_class(self): return f"severity-{self.music_instruments_severity.lower()}"
    @property
    def gambling_severity_css_class(self): return f"severity-{self.gambling_severity.lower()}"
    @property
    def lying_severity_css_class(self): return f"severity-{self.lying_severity.lower()}"
    @property
    def simulate_killing_severity_css_class(self): return f"severity-{self.simulate_killing_severity.lower()}"
    @property
    def simulate_theft_crime_severity_css_class(self): return f"severity-{self.simulate_theft_crime_severity.lower()}"
    @property
    def normalize_haram_rels_severity_css_class(self): return f"severity-{self.normalize_haram_rels_severity.lower()}"
    @property
    def normalize_substances_severity_css_class(self): return f"severity-{self.normalize_substances_severity.lower()}"
    @property
    def profanity_obscenity_severity_css_class(self): return f"severity-{self.profanity_obscenity_severity.lower()}"
    @property
    def time_wasting_severity_css_class(self): return f"severity-{self.time_wasting_severity.lower()}"
    @property
    def financial_extravagance_severity_css_class(self): return f"severity-{self.financial_extravagance_severity.lower()}"
    @property
    def online_communication_severity_css_class(self): return f"severity-{self.online_communication_severity.lower()}"
    @property
    def ugc_risks_severity_css_class(self): return f"severity-{self.ugc_risks_severity.lower()}"


# --- GameComment ---
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
        return _("Comment by %(username)s on %(game_title)s (%(status)s)") % {
            'username': self.user.username, 'game_title': self.game.title, 'status': status
        }
    @property
    def flag_count(self):
        return self.flagged_by.count()

# --- MethodologyPage ---
class MethodologyPage(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('Page Title'))
    content = RichTextUploadingField(verbose_name=_('Page Content'))
    last_updated = models.DateTimeField(auto_now=True, verbose_name=_('Last Updated'))
    class Meta:
        verbose_name = _("Methodology Page")
        verbose_name_plural = _("Methodology Page")
    def __str__(self):
        return self.title

# --- WhyMGCPage ---
class WhyMGCPage(models.Model):
    title = models.CharField(max_length=200, default=_('Why MGC?'), verbose_name=_('Page Title'))
    content = RichTextUploadingField(verbose_name=_('Page Content'))
    last_updated = models.DateTimeField(auto_now=True, verbose_name=_('Last Updated'))
    class Meta:
        verbose_name = _("Why MGC Page")
        verbose_name_plural = _("Why MGC Page")
    def __str__(self):
        return str(self.title)

# --- UserContribution (Per Category) ---
class UserContribution(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='user_contributions', verbose_name=_('Game'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_contributions', verbose_name=_('User'))
    category = models.ForeignKey(Flag, on_delete=models.CASCADE, related_name='user_contributions', verbose_name=_('Content Category'))
    severity_rating = models.CharField(
        max_length=1, choices=Game.SEVERITY_CHOICES, blank=True, null=True, verbose_name=_('User Severity Rating')
    )
    content = models.TextField(
        _('Details / Justification'),
        blank=True,
        help_text=_("Explain your rating for this specific category (e.g., where it occurs, context).")
    )
    is_spoiler = models.BooleanField(default=False, verbose_name=_('Contains Spoilers?'))
    is_approved = models.BooleanField(default=False, verbose_name=_('Approved'))
    moderator_attention_needed = models.BooleanField(default=False, verbose_name=_('Needs Attention'))
    flagged_by = models.ManyToManyField(User, related_name='flagged_contributions', blank=True, verbose_name=_('Flagged By'))
    created_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Date Added'))
    updated_date = models.DateTimeField(auto_now=True, verbose_name=_('Date Updated'))
    class Meta:
        ordering = ['category__description', '-created_date']
        unique_together = ('game', 'user', 'category')
        verbose_name = _('User Contribution (Category)')
        verbose_name_plural = _('User Contributions (Category)')

    def __str__(self):
        status = _('Approved') if self.is_approved else _('Pending')
        if self.moderator_attention_needed: status += f" ({_('Flagged')})"
        category_display = self.category.description if self.category else _('Unknown Category')
        return _("Contribution by %(user)s on %(game)s - Category: %(category)s (%(status)s)") % {
            'user': self.user.username,
            'game': self.game.title,
            'category': category_display,
            'status': status
        }
    @property
    def flag_count(self):
        return self.flagged_by.count()
    def get_severity_rating_display(self):
        return dict(Game.SEVERITY_CHOICES).get(self.severity_rating, '')