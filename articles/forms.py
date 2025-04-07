# articles/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ArticleComment
from django_recaptcha.fields import ReCaptchaField

class ArticleCommentForm(forms.ModelForm):
    captcha = ReCaptchaField()

    class Meta:
        model = ArticleComment
        fields = ['content'] # Only content needed from user in the form
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': _('Add your comment...'),
                'class': 'form-control' # Ensure Bootstrap class is added
                }),
        }
        labels = {
            'content': '', # Hide the default label, placeholder is enough
        }