# ratings/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from urllib.parse import unquote
from django.views.generic import TemplateView

# Import your models and forms
# REMOVED 'Platform' import if it was there previously
from .models import Game, RatingTier, Flag, GameComment, MethodologyPage, WhyMGCPage, Suggestion
from .forms import SignUpForm, GameCommentForm, ContactForm, SuggestionForm, UserUpdateForm
from articles.models import Article # Assuming articles app is used elsewhere

# --- Import django-countries ---
from django_countries import countries

# --- Helper functions (keep as they are) ---
SEVERITY_ORDER = {'N': 0, 'L': 1, 'M': 2, 'S': 3}
DEFAULT_SEVERITY_CODE = 'N'
RISK_SEVERITY_TEXT_MAP = {
    'N': _("No"),
    'L': _("Mild"),
    'M': _("Moderate"),
    'S': _("Severe"),
}

def calculate_risk_summary_for_game(game):
    # ... (keep this function as is) ...
    category_field_map = {
        'A': Game.CATEGORY_A_FIELDS,
        'B': Game.CATEGORY_B_FIELDS,
        'C': Game.CATEGORY_C_FIELDS,
        'D': Game.CATEGORY_D_FIELDS,
    }
    risk_summary_texts = {}
    for cat_prefix, fields in category_field_map.items():
        max_severity_code = DEFAULT_SEVERITY_CODE
        for field_name in fields:
            current_severity = getattr(game, field_name, DEFAULT_SEVERITY_CODE)
            # Treat None explicitly as default severity
            if current_severity is None:
                current_severity = DEFAULT_SEVERITY_CODE

            # Update max severity if current field's severity is higher
            if SEVERITY_ORDER.get(current_severity, 0) > SEVERITY_ORDER.get(max_severity_code, 0):
                max_severity_code = current_severity

        # Map the highest severity code found to its display text
        risk_summary_texts[cat_prefix] = RISK_SEVERITY_TEXT_MAP.get(
            max_severity_code, RISK_SEVERITY_TEXT_MAP[DEFAULT_SEVERITY_CODE]
        )
    return risk_summary_texts

# --- Other Views (homepage, game_list, game_detail, signup, user_profile_edit, delete/flag comments etc.) ---
# Keep these views as they were.

# --- Methodology View ---
def methodology_view(request):
    # ... (keep as is) ...
    methodology_page = MethodologyPage.objects.first()
    if not methodology_page:
        messages.warning(request, _("Methodology page content is not available yet."))
    context = {
        'methodology_page': methodology_page,
        'page_title': methodology_page.title if methodology_page else _('MGC Rating Methodology')
    }
    return render(request, 'ratings/methodology.html', context)


# --- Why MGC View ---
def why_mgc_view(request):
    # ... (keep as is) ...
    why_mgc_page = WhyMGCPage.objects.first()
    if not why_mgc_page:
        messages.warning(request, _("Content for 'Why MGC?' is not available yet."))
    context = {
        'why_mgc_page': why_mgc_page,
        'page_title': why_mgc_page.title if why_mgc_page else _('Why MGC?')
    }
    return render(request, 'ratings/why_mgc.html', context)


# --- Contact View (CORRECTED) ---
def contact_view(request):
    initial_data = {}
    requested_subject = request.GET.get('subject')
    requested_game_title_raw = request.GET.get('game_title')

    if requested_subject == 'GAME_REVIEW_REQUEST':
        initial_data['subject'] = 'GAME_REVIEW_REQUEST'
        message_template = _("I would like to request a review for the game: %(game_title)s\n\nPlease add any details or reasons for the request here:\n\n")
        game_title_display = _("[Please enter game title]")
        if requested_game_title_raw:
            try: game_title_display = unquote(requested_game_title_raw)
            except Exception: game_title_display = _("[Could not decode game title]")
        initial_data['message'] = message_template % {'game_title': game_title_display}

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            from_email = form.cleaned_data['email']
            subject_code = form.cleaned_data['subject']
            message_body = form.cleaned_data['message']
            is_parent = form.cleaned_data.get('is_parent', False)

            # --- FIX: Get country code and look up its name ---
            country_code = form.cleaned_data.get('country') # This gets the code string, e.g., 'AF'
            country_display = countries.name(country_code) if country_code else _('Not Provided')
            # --- END FIX ---

            subject_display = dict(form.fields['subject'].choices).get(subject_code, subject_code) # Get display name for subject

            email_subject = f"[MGC Contact Form] {subject_display}"
            email_message = (
                f"Name: {name}\n"
                f"Email: {from_email}\n"
                f"Country: {country_display}\n" # Use the display name fetched above
                f"Is Parent/Guardian: {'Yes' if is_parent else 'No'}\n"
                f"Subject: {subject_display}\n\n"
                f"Message:\n{message_body}"
            )

            try:
                 # Use actual admin emails from settings
                 recipient_list = [admin_email for admin_name, admin_email in settings.ADMINS] if hasattr(settings, 'ADMINS') and settings.ADMINS else []
                 if not recipient_list and not settings.DEBUG:
                      print("ERROR: ADMINS setting is empty or not configured in production. Contact form email cannot be sent.")
                      messages.error(request, _('Sorry, the site is not configured to send messages currently. Please try again later.'), extra_tags='contact_form form_error') # Add tag
                      # Return here to prevent attempting to send email
                      return render(request, 'ratings/contact.html', {'form': form}) # Re-render form

                 # Send email or print if in DEBUG and no admins
                 if recipient_list:
                     send_mail(
                         email_subject,
                         email_message,
                         settings.DEFAULT_FROM_EMAIL, # Use configured sender
                         recipient_list,
                         fail_silently=False
                     )
                     messages.success(request, _('Thank you for your message! We will get back to you soon.'), extra_tags='contact_form') # Add tag
                     return redirect('ratings:contact_success')
                 elif settings.DEBUG:
                      print(f"--- Contact Form Email (DEBUG: No ADMINS set) ---\nSubject: {email_subject}\nFrom: {from_email}\n{email_message}\n---------------------------------------------------------")
                      messages.success(request, _('[DEBUG] Thank you for your message! (Email would be sent to ADMINS if configured)'), extra_tags='contact_form') # Add tag
                      return redirect('ratings:contact_success')

            except Exception as e:
                # Log the actual error for debugging
                print(f"ERROR sending contact form email: {e}")
                messages.error(request, _('Sorry, there was an error sending your message. Please try again later.'), extra_tags='contact_form form_error') # Add tag

        else: # Form is NOT valid
             # Use the corrected generic error message
             messages.error(request, _('Please correct the errors noted below.'), extra_tags='contact_form form_error') # Add tag
             print(f"Contact form errors: {form.errors.as_json()}") # Log errors for debugging

    else: # GET request
        form = ContactForm(initial=initial_data)

    context = {'form': form}
    return render(request, 'ratings/contact.html', context)


# --- Contact Success View ---
def contact_success_view(request):
    return render(request, 'ratings/contact_success.html')


# --- Other views (delete_suggestion, support_us_view etc.) ---
# Keep these views as they were.
@login_required
@require_POST
def delete_suggestion(request, suggestion_id):
    # ... (keep as is) ...
    suggestion = get_object_or_404(Suggestion.objects.select_related('game', 'user'), pk=suggestion_id)

    if request.user.is_staff:
        referer = request.META.get('HTTP_REFERER')
        admin_url = reverse('admin:ratings_suggestion_changelist')
        if referer and admin_url in referer:
             redirect_url = admin_url
        else:
             redirect_url = suggestion.game.get_absolute_url() + '#user-suggestions' if suggestion.game else admin_url
    else:
        if suggestion.user != request.user:
             messages.error(request, _("You do not have permission to delete this suggestion."))
             return redirect(suggestion.game.get_absolute_url() + '#user-suggestions' if suggestion.game else reverse('home'))
        redirect_url = suggestion.game.get_absolute_url() + '#user-suggestions' if suggestion.game else reverse('home')

    suggestion.delete()
    messages.success(request, _("Suggestion deleted successfully."))
    return redirect(redirect_url)


class SupportUsView(TemplateView):
    # ... (keep as is) ...
    template_name = 'ratings/support_us.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Support MGC")
        # Add any other context needed for the support page (e.g., Patreon link)
        # context['patreon_link'] = "https://www.patreon.com/your_mgc_page" # Example
        return context

support_us_view = SupportUsView.as_view()