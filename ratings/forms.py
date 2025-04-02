# ratings/forms.py (with CAPTCHA)
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import GameComment
from django_recaptcha.fields import ReCaptchaField # <--- Import from the correct app name

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text=_('Required. Please enter a valid email address.')
    )
    captcha = ReCaptchaField() # <--- Change to ReCaptchaField

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("An account with this email already exists."))
        return email

class GameCommentForm(forms.ModelForm):
    captcha = ReCaptchaField() # <--- Change to ReCaptchaField

    class Meta:
        model = GameComment
        fields = ['content'] # Only content and captcha needed from user
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': _('Add your comment...'),
                'class': 'form-control' # Ensure class is added here
                }),
        }
        labels = {
            'content': '', # Hide the default label, placeholder is enough
        }