# ratings/views.py
from django.shortcuts import render, get_object_or_404, redirect, Http404
from django.urls import reverse
from .models import Game, RatingTier, Flag, GameComment, MethodologyPage, WhyMGCPage
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import SignUpForm, GameCommentForm
from django.contrib.auth import login
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext # Keep gettext if used elsewhere
# Removed get_language import as it's usually not needed for basic fetching
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from articles.models import Article


# --- Homepage View (Keep as is) ---
def homepage(request):
    latest_articles = Article.objects.filter(published_date__isnull=False).order_by('-published_date')[:3]
    # Fetch recently added/updated games instead of just Halal
    recent_games = Game.objects.select_related('rating_tier').order_by('-date_updated')[:4] # Show 4 recent games
    # Fetch all tiers for the explanation section
    all_tiers = RatingTier.objects.all()

    context = {
        'recent_games': recent_games, # Pass recent games
        'latest_articles': latest_articles,
        'all_tiers': all_tiers, # Pass all tiers
    }
    return render(request, 'homepage.html', context)

# --- Game List View (Keep as is) ---
def game_list(request, developer_slug=None, publisher_slug=None):
    games_queryset = Game.objects.select_related('rating_tier').prefetch_related('flags').all()
    page_title = _("Game Ratings")
    filter_description = None
    # Developer/Publisher filtering logic
    if developer_slug:
        first_game = games_queryset.filter(developer_slug=developer_slug).first(); dev_name = first_game.developer if first_game else developer_slug
        page_title = gettext("Games by %(developer_name)s") % {'developer_name': dev_name}; filter_description = gettext("Showing games developed by <strong>%(developer_name)s</strong>.") % {'developer_name': dev_name}
        games_queryset = games_queryset.filter(developer_slug=developer_slug)
    elif publisher_slug:
        first_game = games_queryset.filter(publisher_slug=publisher_slug).first(); pub_name = first_game.publisher if first_game else publisher_slug
        page_title = gettext("Games by %(publisher_name)s") % {'publisher_name': pub_name}; filter_description = gettext("Showing games published by <strong>%(publisher_name)s</strong>.") % {'publisher_name': pub_name}
        games_queryset = games_queryset.filter(publisher_slug=publisher_slug)
    # Search and Filter logic
    search_query = request.GET.get('q', ''); selected_tier_code = request.GET.get('tier', ''); selected_flag_symbol = request.GET.get('flag', ''); sort_by = request.GET.get('sort', '-date_added'); selected_platforms = request.GET.getlist('platform')
    if search_query: games_queryset = games_queryset.filter( Q(title__icontains=search_query) | Q(developer__icontains=search_query) | Q(publisher__icontains=search_query) | Q(summary__icontains=search_query) ).distinct()
    if selected_tier_code and selected_tier_code != 'all': games_queryset = games_queryset.filter(rating_tier__tier_code=selected_tier_code).distinct()
    if selected_flag_symbol: games_queryset = games_queryset.filter(flags__symbol=selected_flag_symbol).distinct()
    platform_filters = Q()
    if selected_platforms:
        platform_map = { 'pc': 'available_pc', 'ps5': 'available_ps5', 'ps4': 'available_ps4', 'xbx': 'available_xbox_series', 'xb1': 'available_xbox_one', 'nsw': 'available_switch', 'and': 'available_android', 'ios': 'available_ios', 'qst': 'available_quest' }
        for plat_code in selected_platforms: field_name = platform_map.get(plat_code);
        if field_name: platform_filters |= Q(**{field_name: True})
        if platform_filters: games_queryset = games_queryset.filter(platform_filters).distinct()
    # Sorting
    valid_sort_options = ['title', '-title', 'release_date', '-release_date', 'date_added', '-date_added']; sort_param = sort_by if sort_by in valid_sort_options else '-date_added'
    games_queryset = games_queryset.order_by(sort_param)
    # Pagination
    paginator = Paginator(games_queryset, 12); page_number = request.GET.get('page')
    try: games_page = paginator.page(page_number)
    except PageNotAnInteger: games_page = paginator.page(1)
    except EmptyPage: games_page = paginator.page(paginator.num_pages)
    # Context
    all_tiers = RatingTier.objects.all(); all_flags = Flag.objects.all()
    platform_list_for_template = [ {'code': 'pc', 'name': 'PC'}, {'code': 'ps5', 'name': 'PS5'}, {'code': 'ps4', 'name': 'PS4'}, {'code': 'xbx', 'name': 'Xbox Series'}, {'code': 'xb1', 'name': 'Xbox One'}, {'code': 'nsw', 'name': 'Switch'}, {'code': 'and', 'name': 'Android'}, {'code': 'ios', 'name': 'iOS'}, {'code': 'qst', 'name': 'Quest'}, ]
    context = { 'games_page': games_page, 'page_title': page_title, 'filter_description': filter_description, 'all_tiers': all_tiers, 'all_flags': all_flags, 'search_query': search_query, 'selected_tier': selected_tier_code, 'selected_flag': selected_flag_symbol, 'sort_by': sort_by, 'selected_platforms': selected_platforms, 'platform_list_for_template': platform_list_for_template, }
    return render(request, 'ratings/game_list.html', context)


# --- Game Detail View (Keep as is) ---
def game_detail(request, game_slug):
    game = get_object_or_404(
        Game.objects.select_related('rating_tier').prefetch_related(
            # 'flags', # Removed
            'critic_reviews', 'comments__user', 'comments__flagged_by'
        ),
        slug=game_slug
    )
    all_comments = game.comments.all()
    comment_form = GameCommentForm()
    # Comment handling logic
    if request.method == 'POST':
        if not request.user.is_authenticated: messages.error(request, _("You must be logged in to post a comment.")); return redirect(f"{reverse('login')}?next={request.path}")
        if not request.user.is_active: messages.error(request, _("Your account is currently inactive and cannot post comments."), extra_tags='comment_error'); context = {'game': game, 'all_comments': all_comments, 'comment_form': comment_form}; return render(request, 'ratings/game_detail.html', context)
        comment_form = GameCommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False); new_comment.game = game; new_comment.user = request.user; new_comment.approved = True; new_comment.save()
            messages.success(request, _('Your comment has been posted.'), extra_tags='comment_success')
            return redirect(game.get_absolute_url() + '#comments-section')
        else: messages.error(request, _('There was an error submitting your comment. Please check the form and CAPTCHA.'), extra_tags='comment_error')
    context = { 'game': game, 'all_comments': all_comments, 'comment_form': comment_form, }
    return render(request, 'ratings/game_detail.html', context)

# --- Glossary View (Keep as is) ---
def glossary_view(request):
    all_tiers = RatingTier.objects.all()
    severity_choices_dict = dict(Game.SEVERITY_CHOICES)
    context = { 'all_tiers': all_tiers, 'severity_choices': severity_choices_dict }
    return render(request, 'ratings/glossary.html', context)

# --- Signup View (Keep as is) ---
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST);
        if form.is_valid(): user = form.save(); login(request, user); messages.success(request, _("Registration successful! You are now logged in.")); return redirect('home')
        else: messages.error(request, _("Please correct the errors below, including the CAPTCHA."), extra_tags='form_error')
    else: form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

# --- Delete Comment View (Keep as is) ---
@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(GameComment.objects.select_related('game'), pk=comment_id); game_url = comment.game.get_absolute_url() + '#comments-section'
    if not request.user.is_staff: messages.error(request, _("You do not have permission to delete this comment.")); return redirect(game_url)
    comment_content = comment.content[:30]; comment.delete(); messages.success(request, _("Comment '%(comment_snippet)s...' deleted successfully.") % {'comment_snippet': comment_content}); return redirect(game_url)

# --- Flag Comment View (Keep as is) ---
@login_required
@require_POST
def flag_comment(request, comment_id):
    comment = get_object_or_404(GameComment.objects.select_related('game', 'user'), pk=comment_id); game_url = comment.game.get_absolute_url() + '#comments-section'
    if comment.user == request.user: messages.warning(request, _("You cannot flag your own comment.")); return redirect(game_url)
    if comment.flagged_by.filter(pk=request.user.pk).exists(): messages.info(request, _("You have already flagged this comment.")); return redirect(game_url)
    comment.flagged_by.add(request.user); comment.moderator_attention_needed = True; comment.save(); messages.success(request, _("Comment flagged for moderator review. Thank you.")); return redirect(game_url)

# --- Methodology View
def methodology_view(request):
    methodology_page = None # Initialize to None
    try:
        # Fetch the single MethodologyPage object.
        # Modeltranslation automatically handles fetching the current language's fields.
        methodology_page = MethodologyPage.objects.first()

    except MethodologyPage.DoesNotExist: # Should not happen with .first() but good practice
        messages.warning(request, _("Methodology page content is not available yet."))
        # methodology_page remains None
    except Exception as e: # Catch potential unexpected errors
        messages.error(request, _("An error occurred while loading the methodology page."))
        print(f"Error fetching MethodologyPage: {e}") # Log the error for debugging
        methodology_page = None

    if not methodology_page:
         # Optionally add a message again if it's still None after try block
         # messages.warning(request, _("Methodology page content is not available yet."))
         pass # Already handled in except or just render template with None

    context = {
        'methodology_page': methodology_page,
    }
    return render(request, 'ratings/methodology.html', context)

# --- Why MGC View ---
def why_mgc_view(request):
    why_mgc_page = None # Initialize
    try:
        # Fetch the single WhyMGCPage object, respecting language if modeltranslation is used
        why_mgc_page = WhyMGCPage.objects.first() # Should only be one
    except Exception as e: # Catch potential errors during fetch
        messages.error(request, _("An error occurred while loading the page content."))
        print(f"Error fetching WhyMGCPage: {e}") # Log error

    if not why_mgc_page:
         messages.warning(request, _("Content for 'Why MGC?' is not available yet."))

    context = {
        'why_mgc_page': why_mgc_page,
        # Use the title from the object if found, otherwise default
        'page_title': why_mgc_page.title if why_mgc_page else _('Why MGC?')
    }
    return render(request, 'ratings/why_mgc.html', context)