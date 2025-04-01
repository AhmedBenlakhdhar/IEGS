# ratings/forms.py (with i18n)
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _ # Import for translation

class SignUpForm(UserCreationForm):
    # Override email field to make it required and add help text
    email = forms.EmailField(
        max_length=254,
        required=True, # Make email required
        help_text=_('Required. Please enter a valid email address.') # Use _()
    )
    # Note: Labels for username, password1, password2 come from UserCreationForm
    # and Django handles their translation if its locale files are present.
    # We can override them here with _() if needed for customization.
    # e.g., username = forms.CharField(label=_('Preferred Username'), ...)

    class Meta(UserCreationForm.Meta):
        model = User
        # Define fields explicitly to control order and inclusion
        fields = ('username', 'email') # Removed first/last name for simplicity

    # Optional: Add clean_email method for extra validation if needed
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            # Use _() for validation errors
            raise forms.ValidationError(_("An account with this email already exists."))
        return email

    # If you were overriding clean methods for password validation,
    # you would use _() for those ValidationError messages too.
    # e.g., raise forms.ValidationError(_("Passwords do not match."))