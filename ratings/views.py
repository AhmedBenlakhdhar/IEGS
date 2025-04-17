# ratings/views.py
from django.shortcuts import render, get_object_or_404, redirect, Http404
from django.urls import reverse
from articles.models import Article # Keep article import for homepage
# GameComment and Suggestion are now the relevant user input models
from .models import Game, RatingTier, Flag, GameComment, MethodologyPage, WhyMGCPage, Suggestion
from django.db.models import Q, Count
# Removed defaultdict as contributions_by_category is gone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Added SuggestionForm, removed UserContributionForm
from .forms import SignUpForm, GameCommentForm, ContactForm, SuggestionForm
from django.contrib.auth import login
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from django.conf import settings
# Removed OrderedDict

# --- Homepage View (No changes) ---
def homepage(request):
    latest_articles = Article.objects.filter(published_date__isnull=False).order_by('-published_date')[:3]
    recent_games = Game.objects.select_related('rating_tier').prefetch_related('flags').order_by('-date_updated')[:4]
    all_tiers = RatingTier.objects.all()
    context = { 'recent_games': recent_games, 'latest_articles': latest_articles, 'all_tiers': all_tiers, }
    return render(request, 'homepage.html', context)

# --- Game List View (No changes needed here) ---
def game_list(request, developer_slug=None, publisher_slug=None):
    games_queryset = Game.objects.select_related('rating_tier').prefetch_related('flags').all()
    page_title = _("Game Ratings"); filter_description = None
    if developer_slug:
        first_game = Game.objects.filter(developer_slug=developer_slug).first(); dev_name = first_game.developer if first_game else developer_slug
        page_title = gettext("Games by %(developer_name)s") % {'developer_name': dev_name}; filter_description = gettext("Showing games developed by <strong>%(developer_name)s</strong>.") % {'developer_name': dev_name}
        games_queryset = games_queryset.filter(developer_slug=developer_slug)
    elif publisher_slug:
        first_game = Game.objects.filter(publisher_slug=publisher_slug).first(); pub_name = first_game.publisher if first_game else publisher_slug
        page_title = gettext("Games by %(publisher_name)s") % {'publisher_name': pub_name}; filter_description = gettext("Showing games published by <strong>%(publisher_name)s</strong>.") % {'publisher_name': pub_name}
        games_queryset = games_queryset.filter(publisher_slug=publisher_slug)
    search_query = request.GET.get('q', ''); selected_tier_code = request.GET.get('tier', ''); selected_flag_symbol = request.GET.get('flag', ''); sort_by = request.GET.get('sort', '-date_updated'); selected_platforms = request.GET.getlist('platform')
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
    valid_sort_options = ['title', '-title', 'release_date', '-release_date', 'date_added', '-date_added', 'date_updated', '-date_updated']; sort_param = sort_by if sort_by in valid_sort_options else '-date_updated'; games_queryset = games_queryset.order_by(sort_param)
    paginator = Paginator(games_queryset, 12); page_number = request.GET.get('page')
    try: games_page = paginator.page(page_number)
    except PageNotAnInteger: games_page = paginator.page(1)
    except EmptyPage: games_page = paginator.page(paginator.num_pages)
    all_tiers = RatingTier.objects.all(); all_flags = Flag.objects.all().order_by('description')
    platform_list_for_template = [ {'code': 'pc', 'name': 'PC'}, {'code': 'ps5', 'name': 'PS5'}, {'code': 'ps4', 'name': 'PS4'}, {'code': 'xbx', 'name': 'Xbox Series'}, {'code': 'xb1', 'name': 'Xbox One'}, {'code': 'nsw', 'name': 'Switch'}, {'code': 'and', 'name': 'Android'}, {'code': 'ios', 'name': 'iOS'}, {'code': 'qst', 'name': 'Quest'},]
    context = { 'games_page': games_page, 'page_title': page_title, 'filter_description': filter_description, 'all_tiers': all_tiers, 'all_flags': all_flags, 'search_query': search_query, 'selected_tier': selected_tier_code, 'selected_flag': selected_flag_symbol, 'sort_by': sort_by, 'selected_platforms': selected_platforms, 'platform_list_for_template': platform_list_for_template, }
    return render(request, 'ratings/game_list.html', context)

# --- Game Detail View (UPDATED POST handling and context) ---
def game_detail(request, game_slug):
    game = get_object_or_404(
        Game.objects.select_related('rating_tier').prefetch_related(
            'critic_reviews',
            'flags', # Prefetch auto-assigned flags
            'comments__user', 'comments__flagged_by',
            # REMOVED user_contributions prefetch
        ),
        slug=game_slug
    )
    all_comments = game.comments.all() # Discussion comments
    comment_form = GameCommentForm()
    suggestion_form = SuggestionForm(initial={'game': game}) # Initialize SuggestionForm

    # --- POST Handling ---
    if request.method == 'POST':
        # --- Handle Discussion Comment Submission ---
        if 'submit_comment' in request.POST:
            if not request.user.is_authenticated: messages.error(request, _("You must be logged in to post a comment.")); return redirect(f"{reverse('login')}?next={request.path}#comments-section")
            if not request.user.is_active: messages.error(request, _("Your account is currently inactive and cannot post comments."), extra_tags='comment_error');
            else:
                comment_form = GameCommentForm(data=request.POST)
                if comment_form.is_valid(): new_comment = comment_form.save(commit=False); new_comment.game = game; new_comment.user = request.user; new_comment.approved = True; new_comment.save(); messages.success(request, _('Your comment has been posted.'), extra_tags='comment_success'); return redirect(game.get_absolute_url() + '#comments-section')
                else: messages.error(request, _('There was an error submitting your comment. Please check the form and CAPTCHA.'), extra_tags='comment_error')

        # --- Handle Suggestion Submission ---
        elif 'submit_suggestion' in request.POST:
            # No login required for suggestions now, handled by form field being optional
            # But could add login check if desired:
            # if not request.user.is_authenticated: messages.error(request, _("You must be logged in to submit a suggestion.")); return redirect(f"{reverse('login')}?next={request.path}#suggestion-section")

            suggestion_form = SuggestionForm(request.POST)
            if suggestion_form.is_valid():
                suggestion = suggestion_form.save(commit=False)
                if request.user.is_authenticated:
                    suggestion.user = request.user # Assign user if logged in
                # Game is already set via initial or form data if type requires it
                suggestion.save()
                messages.success(request, _('Thank you! Your suggestion has been submitted for review.'), extra_tags='suggestion_success')
                # Redirect back to the game page, potentially to a specific section
                return redirect(game.get_absolute_url() + '#user-suggestions') # Or just game page
            else:
                messages.error(request, _('Please correct the errors in your suggestion form.'), extra_tags='suggestion_error')
        # --- End Suggestion Handling ---

    # --- Data Preparation for Template ---
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
                    'name': flag.description, 'icon': flag.symbol,
                    'severity_display': game.get_severity_display_name(severity_value),
                    'severity_class': f"severity-{severity_value.lower()}", 'severity_code': severity_value,
                })
    category_names = {'A': _("Risks to Faith"), 'B': _("Prohibition Exposure"), 'C': _("Normalization Risks"), 'D': _("Player Risks"), }
    severity_order = {'N': 0, 'L': 1, 'M': 2, 'S': 3}
    highest_severities = {}
    category_fields = { 'A': Game.CATEGORY_A_FIELDS, 'B': Game.CATEGORY_B_FIELDS, 'C': Game.CATEGORY_C_FIELDS, 'D': Game.CATEGORY_D_FIELDS, }
    for cat_prefix, fields in category_fields.items():
        max_severity_code = 'N'; max_severity_level = 0
        for field_name in fields:
            current_severity = getattr(game, field_name, 'N'); current_level = severity_order.get(current_severity, 0)
            if current_level > max_severity_level: max_severity_level = current_level; max_severity_code = current_severity
        highest_severities[cat_prefix] = max_severity_code
    risk_summary_map = { 'N': _("None"), 'L': _("Mild"), 'M': _("Moderate"), 'S': _("Severe"), }
    risk_summary_texts = { 'A': risk_summary_map.get(highest_severities.get('A', 'N'), _("None")), 'B': risk_summary_map.get(highest_severities.get('B', 'N'), _("None")), 'C': risk_summary_map.get(highest_severities.get('C', 'N'), _("None")), 'D': risk_summary_map.get(highest_severities.get('D', 'N'), _("None")), }

    # REMOVED Community Feedback Data Calculation (contributions_by_category, user_consensus_severity)

    context = {
        'game': game,
        'all_comments': all_comments, # For discussion section
        'comment_form': comment_form, # For discussion section
        'suggestion_form': suggestion_form, # NEW form for suggestions modal/section
        'grouped_mgc_concerns': grouped_mgc_concerns, # For MGC Descriptors display
        'category_names': category_names, # For MGC Descriptors display
        'risk_summary_texts': risk_summary_texts, # For rating graphic block
        'highest_severities': highest_severities, # Needed if template uses it
        'severity_choices_dict': dict(Game.SEVERITY_CHOICES), # For template display names
        'all_flags_info': all_flags_info, # Potentially needed for suggestion form dropdowns if not handled by form itself
        # REMOVED: contributions_by_category, user_consensus_severity
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
            name = form.cleaned_data['name']; from_email = form.cleaned_data['email']; subject = form.cleaned_data['subject']; message_body = form.cleaned_data['message']
            email_subject = f"[MGC Contact Form] {subject}"; email_message = f"Name: {name}\nEmail: {from_email}\n\nMessage:\n{message_body}"
            try:
                 recipient_list = [admin_email for admin_name, admin_email in settings.ADMINS]
                 if not recipient_list: raise ValueError("ADMINS setting is empty in settings.py")
                 send_mail( email_subject, email_message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False )
                 messages.success(request, _('Thank you for your message! We will get back to you soon.'))
                 return redirect('ratings:contact_success')
            except Exception as e: messages.error(request, _('Sorry, there was an error sending your message. Please try again later.')); print(f"Contact form send mail error: {e}")
        else: messages.error(request, _('Please correct the errors below, including the CAPTCHA.'), extra_tags='form_error')
    else: form = ContactForm()
    context = {'form': form}; return render(request, 'ratings/contact.html', context)

# --- Contact Success View (No changes) ---
def contact_success_view(request):
    return render(request, 'ratings/contact_success.html')

# --- REMOVE User Contribution Action Views ---
# @login_required
# @require_POST
# def delete_contribution(request, contribution_id):
#     ... (Old view removed) ...

# @login_required
# @require_POST
# def flag_contribution(request, contribution_id):
#     ... (Old view removed) ...

# --- ADD Suggestion Action Views (Placeholder - implement actual logic if needed) ---
# Note: Currently, there are no frontend buttons/forms to trigger these directly.
# They would likely be used from the admin interface actions initially.
# Adding simple versions for completeness, assuming staff permission is required.

@login_required
@require_POST
def delete_suggestion(request, suggestion_id):
    suggestion = get_object_or_404(Suggestion.objects.select_related('game'), pk=suggestion_id)
    # Decide who can delete: submitter? staff?
    if not request.user.is_staff: # Example: Only staff can delete via this URL
        messages.error(request, _("You do not have permission to delete this suggestion."))
        # Redirect somewhere sensible, maybe admin list or game page if linked
        redirect_url = reverse('admin:ratings_suggestion_changelist') if suggestion.game is None else suggestion.game.get_absolute_url() + '#user-suggestions'
        return redirect(redirect_url)
    suggestion.delete()
    messages.success(request, _("Suggestion deleted successfully."))
    # Redirect somewhere sensible
    redirect_url = reverse('admin:ratings_suggestion_changelist') if suggestion.game is None else suggestion.game.get_absolute_url() + '#user-suggestions'
    return redirect(redirect_url)

# Flagging suggestions might not be necessary if only staff manage them.
# If needed, a similar view `flag_suggestion` could be created.