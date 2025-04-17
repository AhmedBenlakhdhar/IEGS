# ratings/models.py
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from django.core.exceptions import ValidationError
from django.utils import timezone

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
        ordering = ['description']
        verbose_name = _('Content Descriptor')
        verbose_name_plural = _('Content Descriptors')

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

# --- BoycottedEntity ---
class BoycottedEntity(models.Model):
    ENTITY_TYPES = [
        ('DEVELOPER', _('Developer')),
        ('PUBLISHER', _('Publisher')),
    ]
    name = models.CharField(max_length=150, verbose_name=_('Entity Name'), help_text=_("Exact name of the developer or publisher."))
    slug = models.SlugField(max_length=160, blank=True, unique=True, help_text=_("Leave blank to auto-generate."))
    entity_type = models.CharField(max_length=10, choices=ENTITY_TYPES, verbose_name=_('Entity Type'))
    reason = models.TextField(blank=True, verbose_name=_('Reason for Boycott'), help_text=_("Optional: Briefly explain the reason."))
    is_active = models.BooleanField(default=True, verbose_name=_('Boycott Active'), help_text=_("Uncheck to disable this boycott notice without deleting."))
    created_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Date Added'))
    updated_date = models.DateTimeField(auto_now=True, verbose_name=_('Last Updated'))

    class Meta:
        ordering = ['name']
        verbose_name = _('Boycotted Entity')
        verbose_name_plural = _('Boycotted Entities')
        unique_together = ('name', 'entity_type')

    def __str__(self):
        return f"{self.name} ({self.get_entity_type_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.entity_type}")
            self.slug = base_slug
            counter = 1
            while BoycottedEntity.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

# --- Game ---
class Game(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    slug = models.SlugField(max_length=220, unique=True, blank=True, help_text=_("Unique URL-friendly name. Leave blank to auto-generate from title."))
    developer = models.CharField(max_length=100, blank=True, verbose_name=_('Developer'))
    publisher = models.CharField(max_length=100, blank=True, verbose_name=_('Publisher'))
    release_date = models.DateField(blank=True, null=True, verbose_name=_('Release Date'))
    summary = models.TextField(blank=True, help_text=_("Game overview description and overall rating reasoning (used in lists and detail view)."), verbose_name=_('Summary & Rating Rationale'))
    developer_slug = models.SlugField(max_length=110, blank=True, help_text=_("Auto-generated slug for developer filtering."))
    publisher_slug = models.SlugField(max_length=110, blank=True, help_text=_("Auto-generated slug for publisher filtering."))
    available_pc = models.BooleanField(_("Available on PC"), default=False)
    available_ps5 = models.BooleanField(_("Available on PS5"), default=False)
    available_ps4 = models.BooleanField(_("Available on PS4"), default=False)
    available_xbox_series = models.BooleanField(_("Available on Xbox Series X|S"), default=False)
    available_xbox_one = models.BooleanField(_("Available on Xbox One"), default=False)
    available_switch = models.BooleanField(_("Available on Nintendo Switch"), default=False)
    available_android = models.BooleanField(_("Available on Android"), default=False)
    available_ios = models.BooleanField(_("Available on iOS"), default=False)
    available_quest = models.BooleanField(_("Available on Meta Quest"), default=False)
    rating_tier = models.ForeignKey(RatingTier, on_delete=models.PROTECT, related_name='games_rated', null=True, blank=True, help_text=_("Overall MGC Rating calculated based on detailed assessment."), verbose_name=_('Overall Rating Tier'))
    flags = models.ManyToManyField(Flag, blank=True, related_name='games_flagged', help_text=_("Flags automatically assigned based on detailed severity ratings."), verbose_name=_('Content Flags (Auto-assigned)'))
    is_boycotted = models.BooleanField(_("Is Game Specifically Boycotted?"), default=False, help_text=_("Check this if the game itself is subject to a specific boycott, independent of developer/publisher."))
    boycott_reason = models.TextField(_("Game Boycott Reason"), blank=True, null=True, help_text=_("Reason for the game-specific boycott (if applicable)."))

    SEVERITY_CHOICES = [('N', _('None')), ('L', _('Mild')), ('M', _('Moderate')), ('S', _('Severe')), ]
    # A. Risks to Faith
    distorting_islam_severity = models.CharField(_('A1. Distorting Islam'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    promoting_kufr_severity = models.CharField(_('A2. Promoting Kufr/Shirk'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    assuming_divinity_severity = models.CharField(_('A3. Assuming Divinity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    tampering_ghaib_severity = models.CharField(_('A4. Tampering Ghaib'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    deviant_ideologies_severity = models.CharField(_('A5. Deviant Ideologies'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    # B. Prohibition Exposure (Haram Acts)
    gambling_severity = models.CharField(_('B1. Gambling'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    lying_severity = models.CharField(_('B2. Lying'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    indecency_severity = models.CharField(_('B3. Indecency'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    music_instruments_severity = models.CharField(_('B4. Music/Instruments'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    time_waste_severity = models.CharField(_('B5. Time Waste'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    # C. Normalization Risks
    disdain_arrogance_severity = models.CharField(_('C1. Disdain/Arrogance'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    magic_severity = models.CharField(_('C2. Magic'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    intoxicants_severity = models.CharField(_('C3. Intoxicants'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    crime_violence_severity = models.CharField(_('C4. Crime/Violence'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    profanity_severity = models.CharField(_('C5. Profanity'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    # D. Player Risks (General)
    horror_fear_severity = models.CharField(_('D1. Horror/Fear'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    despair_severity = models.CharField(_('D2. Despair'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    spending_severity = models.CharField(_('D3. Spending'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    online_interactions_severity = models.CharField(_('D4. Online Interactions'), max_length=1, choices=SEVERITY_CHOICES, default='N')
    user_content_severity = models.CharField(_('D5. User Content'), max_length=1, choices=SEVERITY_CHOICES, default='N')

    steam_link = models.URLField(_("Steam Store URL"), max_length=300, blank=True, null=True)
    epic_link = models.URLField(_("Epic Games Store URL"), max_length=300, blank=True, null=True)
    gog_link = models.URLField(_("GOG Store URL"), max_length=300, blank=True, null=True)
    other_store_link = models.URLField(_("Other Store URL"), max_length=300, blank=True, null=True)
    critic_reviews = models.ManyToManyField( CriticReview, blank=True, related_name='games', help_text=_("Select critic reviews relevant to this game."), verbose_name=_('Critic Reviews') )
    date_added = models.DateTimeField(auto_now_add=True, verbose_name=_('Date Added'))
    date_updated = models.DateTimeField(auto_now=True, verbose_name=_('Date Updated'))

    SEVERITY_FIELD_TO_FLAG_SYMBOL = {
        'distorting_islam_severity': 'history_edu', 'promoting_kufr_severity': 'hub',
        'assuming_divinity_severity': 'stars', 'tampering_ghaib_severity': 'visibility',
        'deviant_ideologies_severity': 'balance', 'gambling_severity': 'casino',
        'lying_severity': 'front_hand', 'indecency_severity': 'visibility_off',
        'music_instruments_severity': 'music_off', 'time_waste_severity': 'hourglass_top',
        'disdain_arrogance_severity': 'sentiment_dissatisfied', 'magic_severity': 'auto_fix_high',
        'intoxicants_severity': 'local_bar', 'crime_violence_severity': 'local_police',
        'profanity_severity': 'speaker_notes_off', 'horror_fear_severity': 'report',
        'despair_severity': 'sentiment_sad', 'spending_severity': 'monetization_on',
        'online_interactions_severity': 'forum', 'user_content_severity': 'extension',
    }
    CATEGORY_A_FIELDS = [
        'distorting_islam_severity', 'promoting_kufr_severity', 'assuming_divinity_severity',
        'tampering_ghaib_severity', 'deviant_ideologies_severity',
    ]
    CATEGORY_B_FIELDS = [
        'gambling_severity', 'lying_severity', 'indecency_severity',
        'music_instruments_severity', 'time_waste_severity',
    ]
    CATEGORY_C_FIELDS = [
        'disdain_arrogance_severity', 'magic_severity', 'intoxicants_severity',
        'crime_violence_severity', 'profanity_severity',
    ]
    CATEGORY_D_FIELDS = [
        'horror_fear_severity', 'despair_severity', 'spending_severity',
        'online_interactions_severity', 'user_content_severity',
    ]
    ALL_DESCRIPTOR_FIELDS_IN_ORDER = CATEGORY_A_FIELDS + CATEGORY_B_FIELDS + CATEGORY_C_FIELDS + CATEGORY_D_FIELDS

    class Meta:
        ordering = ['-date_updated']
        verbose_name = _('Game')
        verbose_name_plural = _('Games')

    def _calculate_rating_tier(self):
        try:
            tier_kfr = RatingTier.objects.get(tier_code='KFR')
            tier_hrm = RatingTier.objects.get(tier_code='HRM')
            tier_msh = RatingTier.objects.get(tier_code='MSH')
            tier_hal = RatingTier.objects.get(tier_code='HAL')
        except RatingTier.DoesNotExist:
            print(f"ERROR: Rating Tiers missing for calculation in game {self.title}.")
            return None

        if any(getattr(self, field, 'N') == 'S' for field in self.CATEGORY_A_FIELDS):
            return tier_kfr
        if any(getattr(self, field, 'N') == 'M' for field in self.CATEGORY_A_FIELDS) or \
           any(getattr(self, field, 'N') == 'S' for field in self.CATEGORY_B_FIELDS):
            return tier_hrm
        if any(getattr(self, field, 'N') == 'L' for field in self.CATEGORY_A_FIELDS) or \
           any(getattr(self, field, 'N') == 'M' for field in self.CATEGORY_B_FIELDS) or \
           any(getattr(self, field, 'N') in ['M', 'S'] for field in self.CATEGORY_C_FIELDS) or \
           any(getattr(self, field, 'N') == 'S' for field in self.CATEGORY_D_FIELDS):
            return tier_msh
        return tier_hal

    def _get_flags_to_set(self):
        flag_symbols = {
            self.SEVERITY_FIELD_TO_FLAG_SYMBOL[f]
            for f in self.ALL_DESCRIPTOR_FIELDS_IN_ORDER
            if getattr(self, f, 'N') != 'N' and f in self.SEVERITY_FIELD_TO_FLAG_SYMBOL
        }
        return Flag.objects.filter(symbol__in=list(flag_symbols))

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                original = Game.objects.get(pk=self.pk)
                if original.developer != self.developer and hasattr(self, '_developer_boycott_entity_cache'):
                    del self._developer_boycott_entity_cache
                if original.publisher != self.publisher and hasattr(self, '_publisher_boycott_entity_cache'):
                    del self._publisher_boycott_entity_cache
            except Game.DoesNotExist:
                pass

        if not self.slug:
             self.slug = slugify(self.title)
        if self.developer and not self.developer_slug:
            self.developer_slug = slugify(self.developer)
        if self.publisher and not self.publisher_slug:
            self.publisher_slug = slugify(self.publisher)

        # Ensure unique slug if needed
        if not self.pk or Game.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            original_slug = self.slug
            counter = 1
            while Game.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1

        # Calculate and set tier before saving
        calculated_tier = self._calculate_rating_tier()
        if calculated_tier:
            self.rating_tier = calculated_tier
        elif not self.rating_tier_id:
            try:
                self.rating_tier = RatingTier.objects.get(tier_code='MSH')
            except RatingTier.DoesNotExist:
                print(f"ERROR: Cannot set default MSH tier for game '{self.title}'.")

        super().save(*args, **kwargs) # Save the main object

        # Set flags after save (needs PK)
        if self.pk:
            try:
                flags_to_set = self._get_flags_to_set()
                current_flags = set(self.flags.all())
                if set(flags_to_set) != current_flags:
                    self.flags.set(flags_to_set)
            except Exception as e:
                print(f"Error setting flags for game {self.pk} ('{self.title}'): {e}")

    def get_absolute_url(self):
        return reverse('ratings:game_detail', kwargs={'game_slug': self.slug})

    def __str__(self):
        return self.title

    def get_severity_display_name(self, severity_code):
        return dict(self.SEVERITY_CHOICES).get(severity_code, '?')

    # --- Boycott Properties ---
    @property
    def _developer_boycott_info(self):
        if hasattr(self, '_developer_boycott_entity_cache'):
            return self._developer_boycott_entity_cache
        if not self.developer:
            self._developer_boycott_entity_cache = None
            return None
        boycotted_devs = BoycottedEntity.objects.filter(entity_type='DEVELOPER', is_active=True)
        game_dev_lower = self.developer.lower()
        matched_entity = None
        for entity in boycotted_devs:
            if entity.name and entity.name.lower() in game_dev_lower:
                matched_entity = entity
                break
        self._developer_boycott_entity_cache = matched_entity
        return matched_entity

    @property
    def _publisher_boycott_info(self):
        if hasattr(self, '_publisher_boycott_entity_cache'):
            return self._publisher_boycott_entity_cache
        if not self.publisher:
            self._publisher_boycott_entity_cache = None
            return None
        boycotted_pubs = BoycottedEntity.objects.filter(entity_type='PUBLISHER', is_active=True)
        game_pub_lower = self.publisher.lower()
        matched_entity = None
        for entity in boycotted_pubs:
             if entity.name and entity.name.lower() in game_pub_lower:
                matched_entity = entity
                break
        self._publisher_boycott_entity_cache = matched_entity
        return matched_entity

    @property
    def is_developer_boycotted(self):
        return self._developer_boycott_info is not None

    @property
    def is_publisher_boycotted(self):
        return self._publisher_boycott_info is not None

    @property
    def get_developer_boycott_reason(self):
        entity = self._developer_boycott_info
        return entity.reason if entity else None

    @property
    def get_publisher_boycott_reason(self):
        entity = self._publisher_boycott_info
        return entity.reason if entity else None

    @property
    def get_boycotted_developer_name(self):
        entity = self._developer_boycott_info
        return entity.name if entity else None

    @property
    def get_boycotted_publisher_name(self):
        entity = self._publisher_boycott_info
        return entity.name if entity else None

    @property
    def show_boycott_notice(self):
        return self.is_boycotted or self.is_developer_boycotted or self.is_publisher_boycotted

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

# --- Suggestion ---
class Suggestion(models.Model):
    SUGGESTION_TYPES = [
        ('NEW_DESCRIPTOR', _('Suggest New Descriptor')),
        ('CHANGE_SEVERITY', _('Suggest Severity Change')),
        ('OTHER', _('Other Feedback/Correction')),
    ]
    SUGGESTION_STATUS = [
        ('PENDING', _('Pending Review')),
        ('APPROVED', _('Approved')),
        ('IMPLEMENTED', _('Implemented')),
        ('REJECTED', _('Rejected')),
    ]
    suggestion_type = models.CharField(max_length=20, choices=SUGGESTION_TYPES, verbose_name=_('Suggestion Type'))
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='suggestions', verbose_name=_('User (Optional)'))
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True, related_name='suggestions', verbose_name=_('Game (Optional)'))
    existing_descriptor = models.ForeignKey(Flag, on_delete=models.CASCADE, null=True, blank=True, related_name='severity_suggestions', verbose_name=_('Existing Descriptor (if applicable)'))
    current_severity = models.CharField(max_length=1, choices=Game.SEVERITY_CHOICES, blank=True, verbose_name=_('Current Severity (auto-filled)'))
    suggested_severity = models.CharField(max_length=1, choices=Game.SEVERITY_CHOICES, null=True, blank=True, verbose_name=_('Suggested Severity (if applicable)'))
    suggested_descriptor_name = models.CharField(max_length=150, blank=True, verbose_name=_('Suggested Descriptor Name (if new)'))
    suggested_descriptor_icon = models.CharField(max_length=100, blank=True, verbose_name=_('Suggested Icon (optional)'))
    justification = models.TextField(verbose_name=_('Justification / Details'), help_text=_("Please provide details and reasons for your suggestion."))
    status = models.CharField(max_length=15, choices=SUGGESTION_STATUS, default='PENDING', verbose_name=_('Moderation Status'))
    created_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Date Submitted'))
    updated_date = models.DateTimeField(auto_now=True, verbose_name=_('Last Updated'))

    class Meta:
        ordering = ['-created_date']
        verbose_name = _('User Suggestion')
        verbose_name_plural = _('User Suggestions')

    def __str__(self):
        user_str = self.user.username if self.user else _('Anonymous')
        if self.suggestion_type == 'CHANGE_SEVERITY' and self.game and self.existing_descriptor:
            return _("Severity suggestion for '%(descriptor)s' on '%(game)s' by %(user)s") % {
                'descriptor': self.existing_descriptor.description,
                'game': self.game.title,
                'user': user_str
            }
        elif self.suggestion_type == 'NEW_DESCRIPTOR' and self.suggested_descriptor_name:
            return _("New descriptor suggestion '%(name)s' by %(user)s") % {
                'name': self.suggested_descriptor_name,
                'user': user_str
            }
        else:
            return _("Suggestion by %(user)s (%(type)s)") % {
                'user': user_str,
                'type': self.get_suggestion_type_display()
            }

    def clean(self):
        super().clean()
        if self.suggestion_type == 'CHANGE_SEVERITY':
            if not self.game or not self.existing_descriptor or not self.suggested_severity:
                raise ValidationError(_("For severity change suggestions, please specify the game, the descriptor, and the suggested severity."))
            if self.game and self.existing_descriptor:
                field_name = next((fname for fname, fsymbol in Game.SEVERITY_FIELD_TO_FLAG_SYMBOL.items() if fsymbol == self.existing_descriptor.symbol), None)
                if field_name:
                    self.current_severity = getattr(self.game, field_name, 'N')
        elif self.suggestion_type == 'NEW_DESCRIPTOR':
            if not self.suggested_descriptor_name:
                raise ValidationError(_("For new descriptor suggestions, please provide a name."))