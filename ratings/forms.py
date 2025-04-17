# ratings/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
# Removed UserContribution, Added Suggestion
from .models import GameComment, Flag, Game, Suggestion
from django_recaptcha.fields import ReCaptchaField

# --- SignUpForm (No changes) ---
class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text=_('Required. Please enter a valid email address.'))
    captcha = ReCaptchaField()
    class Meta(UserCreationForm.Meta):
        model = User; fields = ('username', 'email')
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
             raise forms.ValidationError(_("An account with this email already exists."))
        return email

# --- GameCommentForm (No changes) ---
class GameCommentForm(forms.ModelForm):
    captcha = ReCaptchaField()
    class Meta:
        model = GameComment; fields = ['content']
        widgets = { 'content': forms.Textarea(attrs={'rows': 3, 'placeholder': _('Add your comment...'), 'class': 'form-control'})}
        labels = { 'content': '' }

# --- ContactForm (No changes) ---
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label=_('Your Name'))
    email = forms.EmailField(required=True, label=_('Your Email'))
    subject = forms.CharField(max_length=150, required=True, label=_('Subject'))
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), required=True, label=_('Message'))
    captcha = ReCaptchaField(label='')

# --- REMOVE UserContributionForm ---
# class UserContributionForm(forms.ModelForm):
#     ... (Old form definition removed) ...

# --- ADD Suggestion Form ---
class SuggestionForm(forms.ModelForm):
    # Make fields required based on suggestion_type (handled in clean method)
    game = forms.ModelChoiceField(
        queryset=Game.objects.all().order_by('title'),
        required=False, # Requirement depends on suggestion_type
        label=_('Game (for Severity Change)'),
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    existing_descriptor = forms.ModelChoiceField(
        queryset=Flag.objects.all().order_by('description'),
        required=False, # Requirement depends on suggestion_type
        label=_('Existing Descriptor (for Severity Change)'),
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
        empty_label=_("-- Select Descriptor --")
    )
    suggested_severity = forms.ChoiceField(
        choices=[('', _('-- Select Severity --'))] + Game.SEVERITY_CHOICES,
        required=False, # Requirement depends on suggestion_type
        label=_('Suggested Severity (for Severity Change)'),
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    suggested_descriptor_name = forms.CharField(
        max_length=150,
        required=False, # Requirement depends on suggestion_type
        label=_('Suggested Descriptor Name (if New)'),
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'})
    )
    # Justification is always required
    justification = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        required=True,
        label=_('Justification / Details')
    )
    captcha = ReCaptchaField(label='') # Add captcha

    class Meta:
        model = Suggestion
        # Define fields to include in the form
        fields = [
            'suggestion_type', 'game', 'existing_descriptor',
            'suggested_severity', 'suggested_descriptor_name',
            'justification', 'captcha' # Add captcha here
        ]
        widgets = {
            'suggestion_type': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        }
        labels = {
            # Adjust labels if needed, defaults are usually fine from model verbose_name
            'suggestion_type': _('Type of Suggestion'),
        }

    # Add custom validation logic
    def clean(self):
        cleaned_data = super().clean()
        suggestion_type = cleaned_data.get('suggestion_type')

        if suggestion_type == 'CHANGE_SEVERITY':
            if not cleaned_data.get('game'):
                self.add_error('game', _("Please select the game for the severity change suggestion."))
            if not cleaned_data.get('existing_descriptor'):
                self.add_error('existing_descriptor', _("Please select the descriptor you want to suggest a change for."))
            if not cleaned_data.get('suggested_severity'):
                self.add_error('suggested_severity', _("Please select the new severity you are suggesting."))
        elif suggestion_type == 'NEW_DESCRIPTOR':
            if not cleaned_data.get('suggested_descriptor_name'):
                self.add_error('suggested_descriptor_name', _("Please provide a name for the new descriptor."))
        # 'OTHER' type only requires justification, which is already required by the field itself.

        return cleaned_data