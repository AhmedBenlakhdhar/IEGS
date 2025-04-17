# ratings/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm # Import PasswordChangeForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import GameComment, Flag, Game, Suggestion
from django_recaptcha.fields import ReCaptchaField
from django_countries.fields import CountryField

# --- User Update Form ---
class UserUpdateForm(forms.ModelForm):
    # Make email required explicitly if it wasn't already in the model
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    # Add first_name/last_name if you want users to edit them
    # first_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        # Specify fields user can edit
        fields = ['username', 'email'] # Add 'first_name', 'last_name' if using them

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if email is already taken by *another* user
        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_("This email address is already in use by another account."))
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Check if username is already taken by *another* user
        if username and User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_("This username is already taken."))
        return username

# --- Password Change Form (Use Django's built-in, maybe override widget attrs later if needed) ---
# We don't need to define it here unless we want to customize it significantly.
# We'll instantiate Django's PasswordChangeForm in the view.

# --- SignUpForm (No changes) ---
class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text=_('Required. Please enter a valid email address.'))
    captcha = ReCaptchaField()
    class Meta(UserCreationForm.Meta): model = User; fields = ('username', 'email')
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists(): raise forms.ValidationError(_("An account with this email already exists."))
        return email

# --- GameCommentForm (No changes) ---
class GameCommentForm(forms.ModelForm):
    captcha = ReCaptchaField()
    class Meta: model = GameComment; fields = ['content']; widgets = { 'content': forms.Textarea(attrs={'rows': 3, 'placeholder': _('Add your comment...'), 'class': 'form-control'})}; labels = { 'content': '' }

# --- SuggestionForm (No changes needed here) ---
class SuggestionForm(forms.ModelForm):
    game = forms.ModelChoiceField(queryset=Game.objects.all().order_by('title'), required=False, label=_('Game (for Severity Change)'), widget=forms.Select(attrs={'class': 'form-select form-select-sm'}))
    existing_descriptor = forms.ModelChoiceField(queryset=Flag.objects.all().order_by('description'), required=False, label=_('Existing Descriptor (for Severity Change)'), widget=forms.Select(attrs={'class': 'form-select form-select-sm'}), empty_label=_("-- Select Descriptor --"))
    suggested_severity = forms.ChoiceField(choices=[('', _('-- Select Severity --'))] + Game.SEVERITY_CHOICES, required=False, label=_('Suggested Severity (for Severity Change)'), widget=forms.Select(attrs={'class': 'form-select form-select-sm'}))
    suggested_descriptor_name = forms.CharField(max_length=150, required=False, label=_('Suggested Descriptor Name (if New)'), widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}))
    justification = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}), required=True, label=_('Justification / Details'))
    captcha = ReCaptchaField(label='')
    class Meta: model = Suggestion; fields = ['suggestion_type', 'game', 'existing_descriptor', 'suggested_severity', 'suggested_descriptor_name', 'justification', 'captcha']; widgets = {'suggestion_type': forms.Select(attrs={'class': 'form-select form-select-sm'}),}; labels = {'suggestion_type': _('Type of Suggestion'),}
    def clean(self):
        cleaned_data = super().clean(); suggestion_type = cleaned_data.get('suggestion_type')
        if suggestion_type == 'CHANGE_SEVERITY':
            if not cleaned_data.get('game'): self.add_error('game', _("Please select the game for the severity change suggestion."))
            if not cleaned_data.get('existing_descriptor'): self.add_error('existing_descriptor', _("Please select the descriptor you want to suggest a change for."))
            if not cleaned_data.get('suggested_severity'): self.add_error('suggested_severity', _("Please select the new severity you are suggesting."))
        elif suggestion_type == 'NEW_DESCRIPTOR':
            if not cleaned_data.get('suggested_descriptor_name'): self.add_error('suggested_descriptor_name', _("Please provide a name for the new descriptor."))
        return cleaned_data

# --- ContactForm (No changes needed here) ---
class ContactForm(forms.Form):
    SUBJECT_CHOICES = [ ('', _('-- Select Subject --')), ('GENERAL_QUESTION', _('General Question')), ('RATING_FEEDBACK', _('Feedback on a Game Rating')), ('METHODOLOGY_QUESTION', _('Question about Methodology')), ('SUGGESTION', _('Suggestion for the Site')), ('TECHNICAL_ISSUE', _('Technical Issue/Bug Report')), ('OTHER', _('Other')), ]
    name = forms.CharField(max_length=100, required=True, label=_('Your Name'))
    email = forms.EmailField(required=True, label=_('Your Email'))
    country = CountryField(blank_label=_('-- Select Country --')).formfield(required=True, label=_('Country'), widget=forms.Select(attrs={'class': 'form-select'}))
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES, required=True, label=_('Subject'))
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), required=True, label=_('Message'))
    is_parent = forms.BooleanField(required=False, label=_('I am a parent/guardian.'))
    captcha = ReCaptchaField(label='')