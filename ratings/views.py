# ratings/views.py
from django.shortcuts import render, get_object_or_404, redirect, Http404
from django.urls import reverse
from articles.models import Article
from .models import Game, RatingTier, Flag, GameComment, MethodologyPage, WhyMGCPage, UserContribution
from django.db.models import Q, Avg, Count, F, Value, CharField, When, Case
from collections import defaultdict
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import SignUpForm, GameCommentForm, ContactForm, UserContributionForm
from django.contrib.auth import login
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden, JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError

# --- Homepage View ---
def homepage(request):
    latest_articles = Article.objects.filter(published_date__isnull=False).order_by('-published_date')[:3]
    recent_games = Game.objects.select_related('rating_tier').order_by('-date_updated')[:4]
    all_tiers = RatingTier.objects.all()
    context = {
        'recent_games': recent_games,
        'latest_articles': latest_articles,
        'all_tiers': all_tiers,
    }
    return render(request, 'homepage.html', context)

# --- Game List View ---
def game_list(request, developer_slug=None, publisher_slug=None):
    games_queryset = Game.objects.select_related('rating_tier').prefetch_related('flags').all()
    page_title = _("Game Ratings")
    filter_description = None

    if developer_slug:
        # Use filter().first() to avoid potential DoesNotExist if slug is invalid but queryset is empty
        first_game = Game.objects.filter(developer_slug=developer_slug).first()
        dev_name = first_game.developer if first_game else developer_slug # Fallback to slug if no game found
        page_title = gettext("Games by %(developer_name)s") % {'developer_name': dev_name}
        filter_description = gettext("Showing games developed by <strong>%(developer_name)s</strong>.") % {'developer_name': dev_name}
        games_queryset = games_queryset.filter(developer_slug=developer_slug)
    elif publisher_slug:
        first_game = Game.objects.filter(publisher_slug=publisher_slug).first()
        pub_name = first_game.publisher if first_game else publisher_slug
        page_title = gettext("Games by %(publisher_name)s") % {'publisher_name': pub_name}
        filter_description = gettext("Showing games published by <strong>%(publisher_name)s</strong>.") % {'publisher_name': pub_name}
        games_queryset = games_queryset.filter(publisher_slug=publisher_slug)

    search_query = request.GET.get('q', '')
    selected_tier_code = request.GET.get('tier', '')
    selected_flag_symbol = request.GET.get('flag', '')
    sort_by = request.GET.get('sort', '-date_added')
    selected_platforms = request.GET.getlist('platform')

    if search_query:
        games_queryset = games_queryset.filter(
            Q(title__icontains=search_query) |
            Q(developer__icontains=search_query) |
            Q(publisher__icontains=search_query) |
            Q(summary__icontains=search_query)
        ).distinct()
    if selected_tier_code and selected_tier_code != 'all':
        games_queryset = games_queryset.filter(rating_tier__tier_code=selected_tier_code).distinct()
    if selected_flag_symbol:
        games_queryset = games_queryset.filter(flags__symbol=selected_flag_symbol).distinct()

    platform_filters = Q()
    if selected_platforms:
        platform_map = {
            'pc': 'available_pc', 'ps5': 'available_ps5', 'ps4': 'available_ps4',
            'xbx': 'available_xbox_series', 'xb1': 'available_xbox_one', 'nsw': 'available_switch',
            'and': 'available_android', 'ios': 'available_ios', 'qst': 'available_quest'
        }
        for plat_code in selected_platforms:
            field_name = platform_map.get(plat_code)
            if field_name:
                platform_filters |= Q(**{field_name: True})
        if platform_filters:
            games_queryset = games_queryset.filter(platform_filters).distinct()

    valid_sort_options = ['title', '-title', 'release_date', '-release_date', 'date_added', '-date_added']
    sort_param = sort_by if sort_by in valid_sort_options else '-date_added'
    games_queryset = games_queryset.order_by(sort_param)

    paginator = Paginator(games_queryset, 12)
    page_number = request.GET.get('page')
    try:
        games_page = paginator.page(page_number)
    except PageNotAnInteger:
        games_page = paginator.page(1)
    except EmptyPage:
        games_page = paginator.page(paginator.num_pages)

    all_tiers = RatingTier.objects.all()
    all_flags = Flag.objects.all()
    platform_list_for_template = [
        {'code': 'pc', 'name': 'PC'}, {'code': 'ps5', 'name': 'PS5'}, {'code': 'ps4', 'name': 'PS4'},
        {'code': 'xbx', 'name': 'Xbox Series'}, {'code': 'xb1', 'name': 'Xbox One'}, {'code': 'nsw', 'name': 'Switch'},
        {'code': 'and', 'name': 'Android'}, {'code': 'ios', 'name': 'iOS'}, {'code': 'qst', 'name': 'Quest'},
    ]
    context = {
        'games_page': games_page, 'page_title': page_title, 'filter_description': filter_description,
        'all_tiers': all_tiers, 'all_flags': all_flags, 'search_query': search_query,
        'selected_tier': selected_tier_code, 'selected_flag': selected_flag_symbol,
        'sort_by': sort_by, 'selected_platforms': selected_platforms,
        'platform_list_for_template': platform_list_for_template,
    }
    return render(request, 'ratings/game_list.html', context)

# --- Game Detail View (REVISED Context) ---
def game_detail(request, game_slug):
    game = get_object_or_404(
        Game.objects.select_related('rating_tier').prefetch_related(
            'critic_reviews',
            'comments__user', 'comments__flagged_by',
            'user_contributions__user', 'user_contributions__flagged_by', 'user_contributions__category'
        ),
        slug=game_slug
    )
    all_comments = game.comments.all()
    comment_form = GameCommentForm()
    contribution_form = UserContributionForm()

    if request.method == 'POST':
        if 'submit_comment' in request.POST:
            if not request.user.is_authenticated: messages.error(request, _("You must be logged in to post a comment.")); return redirect(f"{reverse('login')}?next={request.path}#comments-section")
            if not request.user.is_active: messages.error(request, _("Your account is currently inactive and cannot post comments."), extra_tags='comment_error');
            else:
                comment_form = GameCommentForm(data=request.POST)
                if comment_form.is_valid(): new_comment = comment_form.save(commit=False); new_comment.game = game; new_comment.user = request.user; new_comment.approved = True; new_comment.save(); messages.success(request, _('Your comment has been posted.'), extra_tags='comment_success'); return redirect(game.get_absolute_url() + '#comments-section')
                else: messages.error(request, _('There was an error submitting your comment. Please check the form and CAPTCHA.'), extra_tags='comment_error')

        elif 'submit_contribution' in request.POST:
            if not request.user.is_authenticated: messages.error(request, _("You must be logged in to submit a contribution.")); return redirect(f"{reverse('login')}?next={request.path}#user-contributions-section")
            if not request.user.is_active: messages.error(request, _("Your account is currently inactive and cannot submit contributions."), extra_tags='contribution_error');
            else:
                contribution_form = UserContributionForm(request.POST)
                if contribution_form.is_valid():
                    category = contribution_form.cleaned_data['category']
                    existing_contribution = UserContribution.objects.filter(game=game, user=request.user, category=category).first()
                    try:
                        if existing_contribution:
                            existing_contribution.severity_rating = contribution_form.cleaned_data.get('severity_rating'); existing_contribution.content = contribution_form.cleaned_data.get('content', ''); existing_contribution.is_spoiler = contribution_form.cleaned_data.get('is_spoiler', False); existing_contribution.is_approved = False; existing_contribution.moderator_attention_needed = True; existing_contribution.save()
                            messages.success(request, _('Thank you! Your updated contribution has been submitted for review.'), extra_tags='contribution_success')
                        else:
                            contribution = contribution_form.save(commit=False); contribution.game = game; contribution.user = request.user; contribution.is_approved = False; contribution.moderator_attention_needed = True; contribution.save()
                            messages.success(request, _('Thank you! Your contribution has been submitted for review.'), extra_tags='contribution_success')
                        return redirect(game.get_absolute_url() + '#user-contributions-section')
                    except Exception as e: messages.error(request, _('An unexpected error occurred while saving your contribution.'), extra_tags='contribution_error'); print(f"Contribution save error: {e}")
                else: messages.error(request, _('Please correct the errors in your contribution form.'), extra_tags='contribution_error')

    # --- Data for Display (REVISED) ---
    # MGC Concerns (only non-None severity + flag info)
    mgc_concerns = []
    all_flags_info = Flag.objects.order_by('description') # Fetch flags once
    for field_suffix in Game.CATEGORY_FIELDS_IN_ORDER:
        severity_field = f"{field_suffix}_severity"
        severity_value = getattr(game, severity_field, 'N')
        if severity_value != 'N':
            flag_symbol = Game.SEVERITY_FIELD_TO_FLAG_SYMBOL.get(severity_field)
            flag = next((f for f in all_flags_info if f.symbol == flag_symbol), None)
            if flag:
                mgc_concerns.append({
                    'name': flag.description, # Translatable name from Flag model
                    'icon': flag.symbol,
                    'severity_display': game.get_severity_display_name(severity_value),
                    'severity_class': f"severity-{severity_value.lower()}",
                    'severity_code': severity_value, # Pass the code for comparison
                    # Details and Reason REMOVED
                })

    # Approved user contributions grouped by category
    approved_contributions = game.user_contributions.filter(is_approved=True).select_related('user', 'category').order_by('category__description', 'created_date')
    contributions_by_category = defaultdict(list)
    user_consensus_severity = {} # Calculate actual consensus

    for contrib in approved_contributions:
        contributions_by_category[contrib.category.symbol].append(contrib)

    # Calculate User Consensus (Example: Most Frequent Rating)
    # This logic needs refinement based on desired consensus rules (e.g., threshold, tie-breaking)
    categories_with_contributions = approved_contributions.filter(severity_rating__isnull=False).values('category__symbol').distinct()

    for cat_data in categories_with_contributions:
        category_symbol = cat_data['category__symbol']
        # Find the most frequent non-None severity rating for this category
        ratings = approved_contributions.filter(category__symbol=category_symbol, severity_rating__isnull=False)\
                            .exclude(severity_rating='N')\
                            .values('severity_rating')\
                            .annotate(count=Count('id'))\
                            .order_by('-count', 'severity_rating') # Order by count DESC, then severity ASC (L < M < S)

        if ratings:
            most_frequent = ratings.first()
            # Count total non-None ratings for display
            total_valid_ratings = approved_contributions.filter(category__symbol=category_symbol, severity_rating__isnull=False).exclude(severity_rating='N').count()

            if total_valid_ratings > 0: # Only show consensus if there are valid ratings
                user_consensus_severity[category_symbol] = {
                    'rating': most_frequent['severity_rating'],
                    'rating_display': dict(Game.SEVERITY_CHOICES).get(most_frequent['severity_rating'], '?'),
                    'rating_css_class': f"severity-{most_frequent['severity_rating'].lower()}",
                    'count': most_frequent['count'],
                    'total': total_valid_ratings # Show total valid ratings
                }

    context = {
        'game': game,
        'all_comments': all_comments,
        'comment_form': comment_form,
        'contribution_form': contribution_form,
        'mgc_concerns': mgc_concerns, # Pass list of non-None MGC concerns (without details/reason)
        'contributions_by_category': dict(contributions_by_category),
        'user_consensus_severity': user_consensus_severity,
        'all_flags_info': all_flags_info,
    }
    return render(request, 'ratings/game_detail.html', context)

# --- Glossary View ---
def glossary_view(request):
    all_tiers = RatingTier.objects.all()
    severity_choices_dict = dict(Game.SEVERITY_CHOICES)
    context = { 'all_tiers': all_tiers, 'severity_choices': severity_choices_dict }
    return render(request, 'ratings/glossary.html', context)

# --- Signup View ---
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _("Registration successful! You are now logged in."))
            return redirect('home')
        else:
             messages.error(request, _("Please correct the errors below, including the CAPTCHA."), extra_tags='form_error')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

# --- Delete Comment View ---
@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(GameComment.objects.select_related('game'), pk=comment_id)
    game_url = comment.game.get_absolute_url() + '#comments-section'
    if not request.user.is_staff:
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
    methodology_page = None
    try:
        methodology_page = MethodologyPage.objects.first()
    except Exception as e:
        messages.error(request, _("An error occurred while loading the methodology page."))
        print(f"Error fetching MethodologyPage: {e}")
        methodology_page = None
    if not methodology_page:
        messages.warning(request, _("Methodology page content is not available yet."))
    context = {
        'methodology_page': methodology_page,
        'page_title': methodology_page.title if methodology_page else _('MGC Rating Methodology')
    }
    return render(request, 'ratings/methodology.html', context)

# --- Why MGC View ---
def why_mgc_view(request):
    why_mgc_page = None
    try:
        why_mgc_page = WhyMGCPage.objects.first()
    except Exception as e:
        messages.error(request, _("An error occurred while loading the page content."))
        print(f"Error fetching WhyMGCPage: {e}")
    if not why_mgc_page:
        messages.warning(request, _("Content for 'Why MGC?' is not available yet."))
    context = {
        'why_mgc_page': why_mgc_page,
        'page_title': why_mgc_page.title if why_mgc_page else _('Why MGC?')
    }
    return render(request, 'ratings/why_mgc.html', context)

# --- Contact View ---
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            from_email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message_body = form.cleaned_data['message']
            email_subject = f"[MGC Contact Form] {subject}"
            email_message = f"Name: {name}\nEmail: {from_email}\n\nMessage:\n{message_body}"
            recipient_list = [admin_email for admin_name, admin_email in settings.ADMINS]
            try:
                send_mail( email_subject, email_message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False )
                messages.success(request, _('Thank you for your message! We will get back to you soon.'))
                return redirect('ratings:contact_success')
            except Exception as e:
                messages.error(request, _('Sorry, there was an error sending your message. Please try again later.'))
                print(f"Contact form send mail error: {e}") # Log error
        else:
            messages.error(request, _('Please correct the errors below, including the CAPTCHA.'), extra_tags='form_error')
    else:
        form = ContactForm()
    context = {'form': form}
    return render(request, 'ratings/contact.html', context)

# --- Contact Success View ---
def contact_success_view(request):
    return render(request, 'ratings/contact_success.html')

# --- User Contribution Action Views ---
@login_required
@require_POST
def delete_contribution(request, contribution_id):
    contribution = get_object_or_404(UserContribution.objects.select_related('game', 'user'), pk=contribution_id)
    game_url = contribution.game.get_absolute_url() + '#user-contributions-section'
    if contribution.user != request.user and not request.user.is_staff:
        messages.error(request, _("You do not have permission to delete this contribution."))
        return redirect(game_url)
    contribution.delete()
    messages.success(request, _("Your contribution has been deleted."))
    return redirect(game_url)

@login_required
@require_POST
def flag_contribution(request, contribution_id):
    contribution = get_object_or_404(UserContribution.objects.select_related('game', 'user'), pk=contribution_id)
    game_url = contribution.game.get_absolute_url() + '#user-contributions-section'
    if contribution.user == request.user:
        messages.warning(request, _("You cannot flag your own contribution."))
        return redirect(game_url)
    if contribution.flagged_by.filter(pk=request.user.pk).exists():
        messages.info(request, _("You have already flagged this contribution."))
        return redirect(game_url)
    contribution.flagged_by.add(request.user)
    contribution.moderator_attention_needed = True
    contribution.save()
    messages.success(request, _("Contribution flagged for moderator review. Thank you."))
    return redirect(game_url)