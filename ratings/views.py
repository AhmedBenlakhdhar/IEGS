# ratings/views.py
# (Full file with corrections applied to contact_view)

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
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

# --- Import django-countries ---
from django_countries import countries

# Import your models and forms
from .models import Game, RatingTier, Flag, GameComment, MethodologyPage, WhyMGCPage, Suggestion
from .forms import SignUpForm, GameCommentForm, ContactForm, SuggestionForm, UserUpdateForm
from articles.models import Article # Assuming articles app is used elsewhere

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
    """Calculates the highest severity text display for each category."""
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

# --- Homepage View ---
def homepage(request):
    latest_articles = Article.objects.filter(published_date__isnull=False).order_by('-published_date')[:3]
    recent_games_qs = Game.objects.select_related('rating_tier').prefetch_related('flags').order_by('-date_updated')[:6]
    all_tiers = RatingTier.objects.all()

    recent_games_with_summary = []
    for game in recent_games_qs:
        game.risk_summary_texts = calculate_risk_summary_for_game(game)
        recent_games_with_summary.append(game)

    context = {
        'recent_games': recent_games_with_summary,
        'latest_articles': latest_articles,
        'all_tiers': all_tiers,
    }
    return render(request, 'homepage.html', context)


# --- Game List View ---
def game_list(request, developer_slug=None, publisher_slug=None):
    games_queryset = Game.objects.select_related('rating_tier').prefetch_related('flags').all()
    page_title = _("Game Ratings")
    filter_description_parts = []

    if developer_slug:
        first_game = Game.objects.filter(developer_slug=developer_slug).values('developer').first()
        dev_name = first_game['developer'] if first_game else developer_slug
        page_title = gettext("Games by %(developer_name)s") % {'developer_name': dev_name}
        filter_description_parts.append(gettext("Developed by <strong>%(developer_name)s</strong>") % {'developer_name': dev_name})
        games_queryset = games_queryset.filter(developer_slug=developer_slug)
    elif publisher_slug:
        first_game = Game.objects.filter(publisher_slug=publisher_slug).values('publisher').first()
        pub_name = first_game['publisher'] if first_game else publisher_slug
        page_title = gettext("Games by %(publisher_name)s") % {'publisher_name': pub_name}
        filter_description_parts.append(gettext("Published by <strong>%(publisher_name)s</strong>") % {'publisher_name': pub_name})
        games_queryset = games_queryset.filter(publisher_slug=publisher_slug)

    search_query = request.GET.get('q', '').strip()
    selected_tier_code = request.GET.get('tier', '')
    selected_flag_symbol = request.GET.get('flag', '')
    sort_by = request.GET.get('sort', '-date_updated')
    selected_platform_code = request.GET.get('platform', '')
    selected_iarc = request.GET.get('iarc', '')

    if search_query:
        filter_description_parts.append(gettext("matching search '<strong>%(query)s</strong>'") % {'query': search_query})
        games_queryset = games_queryset.filter(
            Q(title__icontains=search_query) |
            Q(developer__icontains=search_query) |
            Q(publisher__icontains=search_query) |
            Q(summary__icontains=search_query)
        ).distinct()

    if selected_tier_code:
        tier = RatingTier.objects.filter(tier_code=selected_tier_code).first()
        if tier:
            filter_description_parts.append(gettext("in tier <strong>%(tier)s</strong>") % {'tier': tier.display_name})
            games_queryset = games_queryset.filter(rating_tier__tier_code=selected_tier_code).distinct()

    if selected_flag_symbol:
        flag = Flag.objects.filter(symbol=selected_flag_symbol).first()
        if flag:
            filter_description_parts.append(gettext("with flag <strong>%(flag)s</strong>") % {'flag': flag.description})
            games_queryset = games_queryset.filter(flags__symbol=selected_flag_symbol).distinct()

    if selected_iarc:
        iarc_display = dict(Game.IARC_RATINGS).get(selected_iarc)
        if iarc_display:
            filter_description_parts.append(gettext("rated <strong>%(iarc)s</strong>") % {'iarc': iarc_display})
            games_queryset = games_queryset.filter(iarc_rating=selected_iarc).distinct()

    platform_map = {
        'pc': 'available_pc', 'ps5': 'available_ps5', 'ps4': 'available_ps4',
        'xbx': 'available_xbox_series', 'xb1': 'available_xbox_one', 'nsw': 'available_switch',
        'and': 'available_android', 'ios': 'available_ios', 'qst': 'available_quest'
    }
    platform_display_names = {
        'pc': 'PC', 'ps5': 'PS5', 'ps4': 'PS4',
        'xbx': 'Xbox Series', 'xb1': 'Xbox One', 'nsw': 'Switch',
        'and': 'Android', 'ios': 'iOS', 'qst': 'Quest',
    }

    if selected_platform_code:
        field_name = platform_map.get(selected_platform_code)
        if field_name:
            games_queryset = games_queryset.filter(**{field_name: True}).distinct()
            platform_name = platform_display_names.get(selected_platform_code, selected_platform_code)
            filter_description_parts.append(gettext("available on <strong>%(platform)s</strong>") % {'platform': platform_name})

    valid_sort_options = [
        'title', '-title', '-release_date', 'release_date',
        '-date_updated', 'date_updated', 'iarc_rating', '-iarc_rating'
    ]
    sort_param = sort_by if sort_by in valid_sort_options else '-date_updated'
    games_queryset = games_queryset.order_by(sort_param)

    paginator = Paginator(games_queryset, 12)
    page_number = request.GET.get('page')
    try:
        games_page = paginator.page(page_number)
    except PageNotAnInteger:
        games_page = paginator.page(1)
    except EmptyPage:
        games_page = paginator.page(paginator.num_pages)

    for game in games_page.object_list:
        game.risk_summary_texts = calculate_risk_summary_for_game(game)

    all_tiers = RatingTier.objects.all()
    all_flags = Flag.objects.all().order_by('description')
    platform_list_for_template = [
        {'code': code, 'name': name} for code, name in platform_display_names.items()
    ]
    iarc_rating_choices = Game.IARC_RATINGS

    filter_description = None
    if len(filter_description_parts) > 0:
        if developer_slug or publisher_slug:
             base_desc = filter_description_parts[0]
             additional_filters = ", ".join(filter_description_parts[1:])
             if additional_filters:
                  if not base_desc.endswith(" "): base_desc += " "
                  filter_description = f"{base_desc}{gettext('and')} {additional_filters}."
             else:
                  filter_description = base_desc
        else:
            filter_description = gettext("Showing games ") + ", ".join(filter_description_parts) + "."

    selected_platforms_list = [selected_platform_code] if selected_platform_code else []

    context = {
        'games_page': games_page,
        'page_title': page_title,
        'filter_description': filter_description,
        'all_tiers': all_tiers,
        'all_flags': all_flags,
        'search_query': search_query,
        'selected_tier': selected_tier_code,
        'selected_flag': selected_flag_symbol,
        'sort_by': sort_by,
        'selected_platforms': selected_platforms_list,
        'selected_platform': selected_platform_code,
        'platform_list_for_template': platform_list_for_template,
        'iarc_rating_choices': iarc_rating_choices,
        'selected_iarc': selected_iarc,
        'developer_slug': developer_slug,
        'publisher_slug': publisher_slug,
    }
    return render(request, 'ratings/game_list.html', context)


# --- Game Detail View ---
def game_detail(request, game_slug):
    game = get_object_or_404(
        Game.objects.select_related('rating_tier').prefetch_related(
            'critic_reviews', 'flags', 'comments__user', 'comments__flagged_by',
        ), slug=game_slug
    )
    all_comments = game.comments.all()
    comment_form = GameCommentForm()
    suggestion_form = SuggestionForm(initial={'game': game})

    if request.method == 'POST':
        if 'submit_comment' in request.POST:
            if not request.user.is_authenticated:
                messages.error(request, _("You must be logged in to post a comment."))
                return redirect(f"{reverse('login')}?next={request.path}#comments-section")
            if not request.user.is_active:
                messages.error(request, _("Your account is currently inactive and cannot post comments."), extra_tags='comment_error')
            else:
                comment_form = GameCommentForm(data=request.POST)
                if comment_form.is_valid():
                    new_comment = comment_form.save(commit=False)
                    new_comment.game = game
                    new_comment.user = request.user
                    new_comment.approved = True
                    new_comment.save()
                    messages.success(request, _('Your comment has been posted.'), extra_tags='comment_success')
                    return redirect(game.get_absolute_url() + '#comments-section')
                else:
                    messages.error(request, _('There was an error submitting your comment. Please check the form and CAPTCHA.'), extra_tags='comment_error')
        elif 'submit_suggestion' in request.POST:
            suggestion_form = SuggestionForm(request.POST)
            if suggestion_form.is_valid():
                suggestion = suggestion_form.save(commit=False)
                suggestion.game = game
                if request.user.is_authenticated:
                    suggestion.user = request.user
                suggestion.save()
                messages.success(request, _('Thank you! Your suggestion has been submitted for review.'), extra_tags='suggestion_success')
                return redirect(game.get_absolute_url() + '#user-suggestions')
            else:
                messages.error(request, _('Please correct the errors in your suggestion form.'), extra_tags='suggestion_error')

    risk_summary_texts = calculate_risk_summary_for_game(game)
    game.risk_summary_texts = risk_summary_texts

    grouped_mgc_concerns = {'A': [], 'B': [], 'C': [], 'D': []}
    all_flags_info = Flag.objects.order_by('description')
    flag_map = {f.symbol: f for f in all_flags_info}

    def get_category_prefix(field_name):
        if field_name in Game.CATEGORY_A_FIELDS: return 'A'
        if field_name in Game.CATEGORY_B_FIELDS: return 'B'
        if field_name in Game.CATEGORY_C_FIELDS: return 'C'
        if field_name in Game.CATEGORY_D_FIELDS: return 'D'
        return None

    for field_name in Game.ALL_DESCRIPTOR_FIELDS_IN_ORDER:
        severity_value = getattr(game, field_name, 'N')
        if severity_value != 'N':
            flag_symbol = Game.SEVERITY_FIELD_TO_FLAG_SYMBOL.get(field_name)
            flag = flag_map.get(flag_symbol)
            category_prefix = get_category_prefix(field_name)
            if flag and category_prefix:
                grouped_mgc_concerns[category_prefix].append({
                    'name': flag.description,
                    'icon': flag.symbol,
                    'severity_display': game.get_severity_display_name(severity_value),
                    'severity_class': f"severity-{severity_value.lower()}",
                    'severity_code': severity_value,
                })

    category_names = {
        'A': _("Risks to Faith"), 'B': _("Prohibition Exposure"),
        'C': _("Normalization Risks"), 'D': _("Player Risks"),
    }
    severity_order = {'N': 0, 'L': 1, 'M': 2, 'S': 3}
    highest_severities = {}
    category_fields_list = {
        'A': Game.CATEGORY_A_FIELDS, 'B': Game.CATEGORY_B_FIELDS,
        'C': Game.CATEGORY_C_FIELDS, 'D': Game.CATEGORY_D_FIELDS,
    }
    for cat_prefix, fields in category_fields_list.items():
        max_severity_code = 'N'
        max_severity_level = 0
        for field_name in fields:
            current_severity = getattr(game, field_name, 'N')
            current_level = severity_order.get(current_severity, 0)
            if current_level > max_severity_level:
                max_severity_level = current_level
                max_severity_code = current_severity
        highest_severities[cat_prefix] = max_severity_code

    context = {
        'game': game,
        'all_comments': all_comments,
        'comment_form': comment_form,
        'suggestion_form': suggestion_form,
        'grouped_mgc_concerns': grouped_mgc_concerns,
        'category_names': category_names,
        'risk_summary_texts': risk_summary_texts,
        'highest_severities': highest_severities,
        'severity_choices_dict': dict(Game.SEVERITY_CHOICES),
        'all_flags_info': all_flags_info,
    }
    return render(request, 'ratings/game_detail.html', context)


# --- Signup View ---
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _("Registration successful! You are now logged in."))
            next_url = request.GET.get('next', reverse('home'))
            return redirect(next_url)
        else:
            messages.error(request, _("Please correct the errors below, including the CAPTCHA."), extra_tags='form_error')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


# --- User Profile Edit View ---
@login_required
def user_profile_edit(request):
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            password_form = PasswordChangeForm(request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, _('Your profile details were successfully updated.'), extra_tags='profile_success')
                return redirect('ratings:profile_edit')
            else:
                 messages.error(request, _('Please correct the errors in the profile details form.'), extra_tags='profile_error')
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            user_form = UserUpdateForm(instance=request.user)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, _('Your password was successfully updated.'), extra_tags='password_success')
                return redirect('ratings:profile_edit')
            else:
                 messages.error(request, _('Please correct the errors in the password change form.'), extra_tags='password_error')
        else:
            user_form = UserUpdateForm(instance=request.user)
            password_form = PasswordChangeForm(request.user)
    else:
        user_form = UserUpdateForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

    context = {
        'user_form': user_form,
        'password_form': password_form,
    }
    return render(request, 'registration/user_profile_edit.html', context)


# --- Delete Comment View ---
@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(GameComment.objects.select_related('game'), pk=comment_id)
    game_url = comment.game.get_absolute_url() + '#comments-section'
    if comment.user != request.user and not request.user.is_staff:
        messages.error(request, _("You do not have permission to delete this comment."))
        return redirect(game_url)

    comment_content = comment.content[:30]
    comment.delete()
    messages.success(request, _("Comment '%(comment_snippet)s...' deleted successfully.") % {'comment_snippet': comment_content})
    return redirect(game_url)


# --- Flag Comment View ---
@login_required
@require_POST
def flag_comment(request, comment_id):
    comment = get_object_or_404(GameComment.objects.select_related('game', 'user'), pk=comment_id)
    game_url = comment.game.get_absolute_url() + '#comments-section'

    if comment.user == request.user:
        messages.warning(request, _("You cannot flag your own comment."))
        return redirect(game_url)

    if comment.flagged_by.filter(pk=request.user.pk).exists():
        messages.info(request, _("You have already flagged this comment."))
        return redirect(game_url)

    comment.flagged_by.add(request.user)
    comment.moderator_attention_needed = True
    comment.save()

    messages.success(request, _("Comment flagged for moderator review. Thank you."))
    return redirect(game_url)


# --- Methodology View ---
def methodology_view(request):
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
            # Use the countries utility to get the name from the code
            country_display = countries.name(country_code) if country_code else _('Not Provided')
            # --- END FIX ---

            subject_display = dict(form.fields['subject'].choices).get(subject_code, subject_code) # Get display name for subject

            email_subject = f"[MGC Contact Form] {subject_display}"
            email_message = (
                f"Name: {name}\n"
                f"Email: {from_email}\n"
                f"Country: {country_display}\n" # Use the looked-up display name
                f"Is Parent/Guardian: {'Yes' if is_parent else 'No'}\n"
                f"Subject: {subject_display}\n\n"
                f"Message:\n{message_body}"
            )

            try:
                 # Use actual admin emails from settings
                 recipient_list = [admin_email for admin_name, admin_email in settings.ADMINS] if hasattr(settings, 'ADMINS') and settings.ADMINS else []
                 if not recipient_list and not settings.DEBUG:
                      # Log a critical error in production if ADMINS is not set
                      print("CRITICAL ERROR: ADMINS setting is empty or not configured in production. Contact form email cannot be sent.")
                      messages.error(request, _('Sorry, the site administration has not been configured to receive messages. Please try again later or contact support directly.'), extra_tags='contact_form form_error')
                      return render(request, 'ratings/contact.html', {'form': form})

                 # Send email or print if in DEBUG and no admins
                 if recipient_list:
                     send_mail(
                         email_subject,
                         email_message,
                         settings.DEFAULT_FROM_EMAIL, # Use configured sender
                         recipient_list,
                         fail_silently=False
                     )
                     messages.success(request, _('Thank you for your message! We will get back to you soon.'), extra_tags='contact_form')
                     return redirect('ratings:contact_success')
                 elif settings.DEBUG:
                      # Print to console only during development if ADMINS isn't set
                      print(f"--- Contact Form Email (DEBUG: No ADMINS set) ---\nSubject: {email_subject}\nFrom: {from_email}\n{email_message}\n---------------------------------------------------------")
                      messages.success(request, _('[DEBUG] Thank you for your message! (Email would be sent to ADMINS if configured)'), extra_tags='contact_form')
                      return redirect('ratings:contact_success')

            except Exception as e:
                # Log the actual error for debugging
                print(f"ERROR sending contact form email: {e}")
                # Provide a user-friendly error message
                messages.error(request, _('Sorry, there was an error sending your message due to a server issue. Please try again later.'), extra_tags='contact_form form_error')

        else: # Form is NOT valid
             # Use the corrected generic error message
             messages.error(request, _('Please correct the errors noted below.'), extra_tags='contact_form form_error')
             # Log specific errors for easier debugging
             print(f"Contact form validation errors: {form.errors.as_json()}")

    else: # GET request
        form = ContactForm(initial=initial_data)

    context = {'form': form}
    return render(request, 'ratings/contact.html', context)


# --- Contact Success View ---
def contact_success_view(request):
    return render(request, 'ratings/contact_success.html')


# --- Delete Suggestion View ---
@login_required
@require_POST
def delete_suggestion(request, suggestion_id):
    suggestion = get_object_or_404(Suggestion.objects.select_related('game', 'user'), pk=suggestion_id)

    # Determine redirect URL based on user type and referrer
    if request.user.is_staff:
        referer = request.META.get('HTTP_REFERER')
        admin_url = reverse('admin:ratings_suggestion_changelist')
        # Redirect back to admin list if that's where they came from
        if referer and admin_url in referer:
             redirect_url = admin_url
        # Otherwise, redirect to game detail (if applicable) or admin list as fallback
        else:
             redirect_url = suggestion.game.get_absolute_url() + '#user-suggestions' if suggestion.game else admin_url
    else:
        # Regular user can only delete their own suggestions
        if suggestion.user != request.user:
             messages.error(request, _("You do not have permission to delete this suggestion."))
             # Redirect to game detail if possible, otherwise home
             return redirect(suggestion.game.get_absolute_url() + '#user-suggestions' if suggestion.game else reverse('home'))
        # Redirect back to the game page where they likely deleted it from
        redirect_url = suggestion.game.get_absolute_url() + '#user-suggestions' if suggestion.game else reverse('home')

    suggestion.delete()
    messages.success(request, _("Suggestion deleted successfully."))
    return redirect(redirect_url)


# --- Support Page View ---
class SupportUsView(TemplateView):
    template_name = 'ratings/support_us.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("Support MGC")
        # Example: Add Patreon link if available in settings or context
        # context['patreon_link'] = getattr(settings, 'PATREON_LINK', None)
        return context

support_us_view = SupportUsView.as_view()