# ratings/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import GameComment, UserContribution, Flag, Game # Import Flag and Game
from django_recaptcha.fields import ReCaptchaField

# --- SignUpForm ---
class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text=_('Required. Please enter a valid email address.')
    )
    captcha = ReCaptchaField()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # It's good practice to handle potential None values, although required=True should prevent it
        if email and User.objects.filter(email=email).exists():
             raise forms.ValidationError(_("An account with this email already exists."))
        return email

# --- GameCommentForm ---
class GameCommentForm(forms.ModelForm):
    captcha = ReCaptchaField()

    class Meta:
        model = GameComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': _('Add your comment...'),
                'class': 'form-control'
                }),
        }
        labels = {
            'content': '',
        }

# --- ContactForm ---
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label=_('Your Name'))
    email = forms.EmailField(required=True, label=_('Your Email'))
    subject = forms.CharField(max_length=150, required=True, label=_('Subject'))
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), required=True, label=_('Message'))
    captcha = ReCaptchaField(label='')

# --- User Contribution Form (Per Category) ---
class UserContributionForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Flag.objects.all().order_by('description'),
        required=True,
        label=_('Content Category'),
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
        empty_label=_("-- Select Category --")
    )
    severity_rating = forms.ChoiceField(
        choices= [('', _('-- Select Severity --'))] + Game.SEVERITY_CHOICES,
        required=False,
        label=_('Your Severity Rating'),
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    is_spoiler = forms.BooleanField(required=False, label=_('Mark review as containing spoilers?'))

    class Meta:
        model = UserContribution
        fields = ['category', 'severity_rating', 'content', 'is_spoiler']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': _('Explain your rating for this specific category (e.g., where it occurs, context, how to avoid)...'),
                'class': 'form-control'
            }),
        }
        labels = {
            'content': _('Details / Justification / Context (Optional)'),
        }

    def clean(self):
        cleaned_data = super().clean()
        severity_rating = cleaned_data.get('severity_rating')
        content = cleaned_data.get('content')

        if not severity_rating and not content:
            raise forms.ValidationError(
                _("Please provide either a severity rating or details for the selected category (or both)."),
                code='rating_or_content_required'
            )
        return cleaned_data
# --- END: User Contribution Form ---