# ratings/views.py
from django.shortcuts import render, get_object_or_404, redirect, Http404
from django.urls import reverse, reverse_lazy
from articles.models import Article
from .models import Game, RatingTier, Flag, GameComment, MethodologyPage, WhyMGCPage, Suggestion
from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import SignUpForm, GameCommentForm, ContactForm, SuggestionForm, UserUpdateForm
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError

# Helper function to calculate risk summary for a game object
def calculate_risk_summary_for_game(game):
    """Calculates the highest severity text for each category for a given game."""
    severity_order = {'N': 0, 'L': 1, 'M': 2, 'S': 3}
    highest_severities = {}
    category_fields = {
        'A': Game.CATEGORY_A_FIELDS, 'B': Game.CATEGORY_B_FIELDS,
        'C': Game.CATEGORY_C_FIELDS, 'D': Game.CATEGORY_D_FIELDS,
    }
    risk_summary_map = { 'N': _("None"), 'L': _("Mild"), 'M': _("Moderate"), 'S': _("Severe"), }
    risk_summary_texts = {}

    for cat_prefix, fields in category_fields.items():
        max_severity_code = 'N'
        max_severity_level = 0
        for field_name in fields:
            current_severity = getattr(game, field_name, 'N')
            current_level = severity_order.get(current_severity, 0)
            if current_level > max_severity_level:
                max_severity_level = current_level
                max_severity_code = current_severity
        highest_severities[cat_prefix] = max_severity_code
        # Directly calculate text here
        risk_summary_texts[cat_prefix] = risk_summary_map.get(max_severity_code, _("None"))

    return risk_summary_texts


# --- Homepage View (Calculate risk summary for recent games) ---
def homepage(request):
    latest_articles = Article.objects.filter(published_date__isnull=False).order_by('-published_date')[:3]
    recent_games_qs = Game.objects.select_related('rating_tier').prefetch_related('flags').order_by('-date_updated')[:4]
    all_tiers = RatingTier.objects.all()

    # Calculate risk summary for each recent game
    recent_games_with_summary = []
    for game in recent_games_qs:
        game.risk_summary_texts = calculate_risk_summary_for_game(game)
        recent_games_with_summary.append(game)

    context = {
        # Use the list with augmented game objects
        'recent_games': recent_games_with_summary,
        'latest_articles': latest_articles,
        'all_tiers': all_tiers,
    }
    return render(request, 'homepage.html', context)

# --- Game List View (Calculate risk summary for paginated games) ---
def game_list(request, developer_slug=None, publisher_slug=None):
    games_queryset = Game.objects.select_related('rating_tier').prefetch_related('flags').all()
    page_title = _("Game Ratings"); filter_description = None
    # (Filtering logic remains the same...)
    if developer_slug:
        first_game = Game.objects.filter(developer_slug=developer_slug).first(); dev_name = first_game.developer if first_game else developer_slug
        page_title = gettext("Games by %(developer_name)s") % {'developer_name': dev_name}; filter_description = gettext("Showing games developed by <strong>%(developer_name)s</strong>.") % {'developer_name': dev_name}
        games_queryset = games_queryset.filter(developer_slug=developer_slug)
    elif publisher_slug:
        first_game = Game.objects.filter(publisher_slug=publisher_slug).first(); pub_name = first_game.publisher if first_game else publisher_slug
        page_title = gettext("Games by %(publisher_name)s") % {'publisher_name': pub_name}; filter_description = gettext("Showing games published by <strong>%(publisher_name)s</strong>.") % {'publisher_name': pub_name}
        games_queryset = games_queryset.filter(publisher_slug=publisher_slug)
    search_query = request.GET.get('q',''); selected_tier_code = request.GET.get('tier',''); selected_flag_symbol = request.GET.get('flag',''); sort_by = request.GET.get('sort','-date_updated'); selected_platforms = request.GET.getlist('platform')
    if search_query: games_queryset = games_queryset.filter( Q(title__icontains=search_query) | Q(developer__icontains=search_query) | Q(publisher__icontains=search_query) | Q(summary__icontains=search_query)).distinct()
    if selected_tier_code and selected_tier_code != 'all': games_queryset = games_queryset.filter(rating_tier__tier_code=selected_tier_code).distinct()
    if selected_flag_symbol: games_queryset = games_queryset.filter(flags__symbol=selected_flag_symbol).distinct()
    platform_filters = Q()
    if selected_platforms:
        platform_map = { 'pc': 'available_pc', 'ps5': 'available_ps5', 'ps4': 'available_ps4', 'xbx': 'available_xbox_series', 'xb1': 'available_xbox_one', 'nsw': 'available_switch', 'and': 'available_android', 'ios': 'available_ios', 'qst': 'available_quest'}
        for plat_code in selected_platforms:
            field_name = platform_map.get(plat_code)
            if field_name: platform_filters |= Q(**{field_name: True})
        if platform_filters: games_queryset = games_queryset.filter(platform_filters).distinct()
    valid_sort_options = ['title','-title','release_date','-release_date','date_added','-date_added','date_updated','-date_updated']; sort_param = sort_by if sort_by in valid_sort_options else '-date_updated'; games_queryset = games_queryset.order_by(sort_param)

    paginator = Paginator(games_queryset, 12); page_number = request.GET.get('page')
    try: games_page = paginator.page(page_number)
    except PageNotAnInteger: games_page = paginator.page(1)
    except EmptyPage: games_page = paginator.page(paginator.num_pages)

    # Calculate risk summary for each game on the current page
    for game in games_page.object_list:
        game.risk_summary_texts = calculate_risk_summary_for_game(game)

    all_tiers = RatingTier.objects.all(); all_flags = Flag.objects.all().order_by('description')
    platform_list_for_template = [ {'code': 'pc', 'name': 'PC'}, {'code': 'ps5', 'name': 'PS5'}, {'code': 'ps4', 'name': 'PS4'}, {'code': 'xbx', 'name': 'Xbox Series'}, {'code': 'xb1', 'name': 'Xbox One'}, {'code': 'nsw', 'name': 'Switch'}, {'code': 'and', 'name': 'Android'}, {'code': 'ios', 'name': 'iOS'}, {'code': 'qst', 'name': 'Quest'},]
    context = {
        'games_page': games_page, # Pass the augmented Page object
        'page_title': page_title, 'filter_description': filter_description,
        'all_tiers': all_tiers, 'all_flags': all_flags, 'search_query': search_query,
        'selected_tier': selected_tier_code, 'selected_flag': selected_flag_symbol,
        'sort_by': sort_by, 'selected_platforms': selected_platforms,
        'platform_list_for_template': platform_list_for_template,
    }
    return render(request, 'ratings/game_list.html', context)


# --- Game Detail View (Calculation already happens here) ---
def game_detail(request, game_slug):
    game = get_object_or_404(
        Game.objects.select_related('rating_tier').prefetch_related(
            'critic_reviews','flags', 'comments__user', 'comments__flagged_by',
        ), slug=game_slug
    )
    all_comments = game.comments.all(); comment_form = GameCommentForm(); suggestion_form = SuggestionForm(initial={'game': game})

    if request.method == 'POST': # ... (POST handling remains the same) ...
        if 'submit_comment' in request.POST:
            if not request.user.is_authenticated: messages.error(request, _("You must be logged in to post a comment.")); return redirect(f"{reverse('login')}?next={request.path}#comments-section")
            if not request.user.is_active: messages.error(request, _("Your account is currently inactive and cannot post comments."), extra_tags='comment_error');
            else:
                comment_form = GameCommentForm(data=request.POST)
                if comment_form.is_valid(): new_comment = comment_form.save(commit=False); new_comment.game = game; new_comment.user = request.user; new_comment.approved = True; new_comment.save(); messages.success(request, _('Your comment has been posted.'), extra_tags='comment_success'); return redirect(game.get_absolute_url() + '#comments-section')
                else: messages.error(request, _('There was an error submitting your comment. Please check the form and CAPTCHA.'), extra_tags='comment_error')
        elif 'submit_suggestion' in request.POST:
            suggestion_form = SuggestionForm(request.POST)
            if suggestion_form.is_valid():
                suggestion = suggestion_form.save(commit=False)
                if request.user.is_authenticated: suggestion.user = request.user
                suggestion.save(); messages.success(request, _('Thank you! Your suggestion has been submitted for review.'), extra_tags='suggestion_success')
                return redirect(game.get_absolute_url() + '#user-suggestions')
            else: messages.error(request, _('Please correct the errors in your suggestion form.'), extra_tags='suggestion_error')

    # --- Data Preparation for Template ---
    # Calculation of risk_summary_texts already happens here
    risk_summary_texts = calculate_risk_summary_for_game(game)
    game.risk_summary_texts = risk_summary_texts
    # Other calculations remain the same...
    grouped_mgc_concerns = {'A': [], 'B': [], 'C': [], 'D': []}; all_flags_info = Flag.objects.order_by('description'); flag_map = {f.symbol: f for f in all_flags_info}
    def get_category_prefix(field_name):
        if field_name in Game.CATEGORY_A_FIELDS: return 'A'
        if field_name in Game.CATEGORY_B_FIELDS: return 'B'
        if field_name in Game.CATEGORY_C_FIELDS: return 'C'
        if field_name in Game.CATEGORY_D_FIELDS: return 'D'
        return None
    for field_name in Game.ALL_DESCRIPTOR_FIELDS_IN_ORDER:
        severity_value = getattr(game, field_name, 'N')
        if severity_value != 'N':
            flag_symbol = Game.SEVERITY_FIELD_TO_FLAG_SYMBOL.get(field_name); flag = flag_map.get(flag_symbol); category_prefix = get_category_prefix(field_name)
            if flag and category_prefix: grouped_mgc_concerns[category_prefix].append({'name': flag.description, 'icon': flag.symbol, 'severity_display': game.get_severity_display_name(severity_value), 'severity_class': f"severity-{severity_value.lower()}", 'severity_code': severity_value,})
    category_names = {'A': _("Risks to Faith"), 'B': _("Prohibition Exposure"), 'C': _("Normalization Risks"), 'D': _("Player Risks"), }; severity_order = {'N': 0, 'L': 1, 'M': 2, 'S': 3}; highest_severities = {}
    category_fields = { 'A': Game.CATEGORY_A_FIELDS, 'B': Game.CATEGORY_B_FIELDS, 'C': Game.CATEGORY_C_FIELDS, 'D': Game.CATEGORY_D_FIELDS, }
    for cat_prefix, fields in category_fields.items():
        max_severity_code = 'N'; max_severity_level = 0
        for field_name in fields: current_severity = getattr(game, field_name, 'N'); current_level = severity_order.get(current_severity, 0);
        if current_level > max_severity_level: max_severity_level = current_level; max_severity_code = current_severity
        highest_severities[cat_prefix] = max_severity_code

    context = {
        'game': game, 'all_comments': all_comments, 'comment_form': comment_form,
        'suggestion_form': suggestion_form, 'grouped_mgc_concerns': grouped_mgc_concerns,
        'category_names': category_names,
        'risk_summary_texts': risk_summary_texts, # Pass the calculated dictionary
        'highest_severities': highest_severities,
        'severity_choices_dict': dict(Game.SEVERITY_CHOICES),
        'all_flags_info': all_flags_info,
    }
    return render(request, 'ratings/game_detail.html', context)

# --- Glossary View (No changes) ---
def glossary_view(request):
    all_tiers = RatingTier.objects.all(); severity_choices_dict = dict(Game.SEVERITY_CHOICES)
    context = { 'all_tiers': all_tiers, 'severity_choices': severity_choices_dict }
    return render(request, 'ratings/glossary.html', context)

# --- Signup View (No changes) ---
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid(): user = form.save(); login(request, user); messages.success(request, _("Registration successful! You are now logged in.")); return redirect('home')
        else: messages.error(request, _("Please correct the errors below, including the CAPTCHA."), extra_tags='form_error')
    else: form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def user_profile_edit(request):
    if request.method == 'POST':
        # Determine which form was submitted
        if 'update_profile' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            password_form = PasswordChangeForm(request.user) # Keep password form instance for re-rendering
            if user_form.is_valid():
                user_form.save()
                messages.success(request, _('Your profile details were successfully updated.'), extra_tags='profile_success')
                return redirect('ratings:profile_edit') # Redirect to same page
            else:
                 messages.error(request, _('Please correct the errors in the profile details form.'), extra_tags='profile_error')

        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            user_form = UserUpdateForm(instance=request.user) # Keep user form instance for re-rendering
            if password_form.is_valid():
                user = password_form.save()
                # Important: Update the session hash to prevent the user from being logged out
                update_session_auth_hash(request, user)
                messages.success(request, _('Your password was successfully updated.'), extra_tags='password_success')
                return redirect('ratings:profile_edit') # Redirect to same page
            else:
                 messages.error(request, _('Please correct the errors in the password change form.'), extra_tags='password_error')
        else:
            # Should not happen with named buttons, but handle just in case
            user_form = UserUpdateForm(instance=request.user)
            password_form = PasswordChangeForm(request.user)
            messages.warning(request, _('Unknown form submission.'))

    else: # GET request
        user_form = UserUpdateForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

    context = {
        'user_form': user_form,
        'password_form': password_form,
    }
    return render(request, 'registration/user_profile_edit.html', context)

# --- Delete Comment View (No changes) ---
@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(GameComment.objects.select_related('game'), pk=comment_id); game_url = comment.game.get_absolute_url() + '#comments-section'
    if not request.user.is_staff: messages.error(request, _("You do not have permission to delete this comment.")); return redirect(game_url)
    comment_content = comment.content[:30]; comment.delete(); messages.success(request, _("Comment '%(comment_snippet)s...' deleted successfully.") % {'comment_snippet': comment_content}); return redirect(game_url)

# --- Flag Comment View (No changes) ---
@login_required
@require_POST
def flag_comment(request, comment_id):
    comment = get_object_or_404(GameComment.objects.select_related('game', 'user'), pk=comment_id); game_url = comment.game.get_absolute_url() + '#comments-section'
    if comment.user == request.user: messages.warning(request, _("You cannot flag your own comment.")); return redirect(game_url)
    if comment.flagged_by.filter(pk=request.user.pk).exists(): messages.info(request, _("You have already flagged this comment.")); return redirect(game_url)
    comment.flagged_by.add(request.user); comment.moderator_attention_needed = True; comment.save(); messages.success(request, _("Comment flagged for moderator review. Thank you.")); return redirect(game_url)

# --- Methodology View (No changes) ---
def methodology_view(request):
    methodology_page = None
    try: methodology_page = MethodologyPage.objects.first()
    except Exception as e: messages.error(request, _("An error occurred while loading the methodology page.")); print(f"Error fetching MethodologyPage: {e}"); methodology_page = None
    if not methodology_page: messages.warning(request, _("Methodology page content is not available yet."))
    context = { 'methodology_page': methodology_page, 'page_title': methodology_page.title if methodology_page else _('MGC Rating Methodology') }
    return render(request, 'ratings/methodology.html', context)

# --- Why MGC View (No changes) ---
def why_mgc_view(request):
    why_mgc_page = None
    try: why_mgc_page = WhyMGCPage.objects.first()
    except Exception as e: messages.error(request, _("An error occurred while loading the page content.")); print(f"Error fetching WhyMGCPage: {e}")
    if not why_mgc_page: messages.warning(request, _("Content for 'Why MGC?' is not available yet."))
    context = { 'why_mgc_page': why_mgc_page, 'page_title': why_mgc_page.title if why_mgc_page else _('Why MGC?') }
    return render(request, 'ratings/why_mgc.html', context)

# --- Contact View (No changes) ---
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            from_email = form.cleaned_data['email']
            # Get the Country object from django-countries
            country_obj = form.cleaned_data.get('country')
            country_display = country_obj.name if country_obj else _('N/A') # Use .name attribute

            subject_code = form.cleaned_data['subject']
            subject_display = dict(form.fields['subject'].choices).get(subject_code, subject_code)
            message_body = form.cleaned_data['message']
            is_parent = form.cleaned_data.get('is_parent', False)

            # Construct email content including country display name
            email_subject = f"[MGC Contact Form] {subject_display}"
            email_message = f"Name: {name}\n"
            email_message += f"Email: {from_email}\n"
            email_message += f"Country: {country_display}\n" # Now using the country name
            email_message += f"Is Parent/Guardian: {'Yes' if is_parent else 'No'}\n"
            email_message += f"Subject: {subject_display}\n\n"
            email_message += f"Message:\n{message_body}"

            try:
                 # Ensure ADMINS is configured in settings
                 # Use settings.ADMINS for recipient list
                 recipient_list = [admin_email for admin_name, admin_email in settings.ADMINS] if hasattr(settings, 'ADMINS') else []
                 if not recipient_list and not settings.DEBUG: # Don't fail loudly in production if ADMINS isn't set, maybe log instead
                      print("WARNING: ADMINS setting is not configured in settings.py. Contact form email not sent.")
                      # Optionally, set a default recipient if needed for testing/fallback
                      # recipient_list = ['fallback@example.com']
                      # Or raise error only if recipient_list is truly empty
                      # raise ValueError("ADMINS setting is empty in settings.py")

                 # Send email only if recipients are available
                 if recipient_list:
                     send_mail(
                         email_subject,
                         email_message,
                         settings.DEFAULT_FROM_EMAIL, # Ensure this is set in settings
                         recipient_list,
                         fail_silently=False
                     )
                 else:
                      # If in DEBUG mode, print to console as EMAIL_BACKEND is console anyway
                      if settings.DEBUG:
                          print("--- Contact Form Email (DEBUG: No ADMINS configured) ---")
                          print(f"Subject: {email_subject}")
                          print(email_message)
                          print("---------------------------------------------------------")
                      # If not DEBUG, it was already warned above.

                 messages.success(request, _('Thank you for your message! We will get back to you soon.'))
                 return redirect('ratings:contact_success')
            except Exception as e:
                messages.error(request, _('Sorry, there was an error sending your message. Please try again later.'))
                print(f"Contact form send mail error: {e}") # Log detailed error
        else:
             messages.error(request, _('Please correct the errors below, including the CAPTCHA.'), extra_tags='form_error')
    else:
        form = ContactForm()
    context = {'form': form}
    return render(request, 'ratings/contact.html', context)

# --- Contact Success View (No changes) ---
def contact_success_view(request):
    return render(request, 'ratings/contact_success.html')

# --- Suggestion Action Views (Keep placeholders) ---
@login_required
@require_POST
def delete_suggestion(request, suggestion_id):
    suggestion = get_object_or_404(Suggestion.objects.select_related('game'), pk=suggestion_id)
    if not request.user.is_staff: messages.error(request, _("You do not have permission to delete this suggestion.")); redirect_url = reverse('admin:ratings_suggestion_changelist') if suggestion.game is None else suggestion.game.get_absolute_url() + '#user-suggestions'; return redirect(redirect_url)
    suggestion.delete(); messages.success(request, _("Suggestion deleted successfully."))
    redirect_url = reverse('admin:ratings_suggestion_changelist') if suggestion.game is None else suggestion.game.get_absolute_url() + '#user-suggestions'
    return redirect(redirect_url)