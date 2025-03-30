# ratings/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _ # Import for translation

class SignUpForm(UserCreationForm):
    # Override email field to make it required and add help text
    email = forms.EmailField(
        max_length=254,
        required=True, # Make email required
        help_text=_('Required. Please enter a valid email address.')
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # Define fields explicitly to control order and inclusion
        fields = ('username', 'email') # Removed first/last name for simplicity

    # Optional: Add clean_email method for extra validation if needed
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("An account with this email already exists."))
        return email