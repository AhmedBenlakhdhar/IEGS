# ratings/views.py - FULL FILE (with comment actions, CAPTCHA check)
from django.shortcuts import render, get_object_or_404, redirect, Http404
from django.urls import reverse
from .models import Game, RatingTier, Flag, GameComment
from articles.models import Article
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import SignUpForm, GameCommentForm
from django.contrib.auth import login
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.shortcuts import render

# ... (homepage and game_list views remain the same as previous version) ...
# --- Homepage View ---
def homepage(request):
    latest_articles = Article.objects.filter(published_date__isnull=False).order_by('-published_date')[:3]
    top_halal_games = Game.objects.select_related('rating_tier').filter(
        rating_tier__tier_code='HAL'
    ).order_by('-release_date', '-date_added')[:3]
    context = {
        'top_halal_games': top_halal_games,
        'latest_articles': latest_articles,
    }
    return render(request, 'homepage.html', context)

# --- Game List View ---
def game_list(request, developer_slug=None, publisher_slug=None):
    games_queryset = Game.objects.select_related('rating_tier').prefetch_related('flags').all()
    page_title = _("Game Ratings")
    filter_description = None

    if developer_slug:
        games_queryset = games_queryset.filter(developer_slug=developer_slug)
        first_game = games_queryset.first()
        dev_name = first_game.developer if first_game else developer_slug
        page_title = gettext("Games by %(developer_name)s") % {'developer_name': dev_name}
        filter_description = gettext("Showing games developed by <strong>%(developer_name)s</strong>.") % {'developer_name': dev_name}
    elif publisher_slug:
        games_queryset = games_queryset.filter(publisher_slug=publisher_slug)
        first_game = games_queryset.first()
        pub_name = first_game.publisher if first_game else publisher_slug
        page_title = gettext("Games by %(publisher_name)s") % {'publisher_name': pub_name}
        filter_description = gettext("Showing games published by <strong>%(publisher_name)s</strong>.") % {'publisher_name': pub_name}

    search_query = request.GET.get('q', '')
    selected_tier = request.GET.get('tier', '')
    selected_flag = request.GET.get('flag', '')
    requires_adjustment_filter = request.GET.get('adj', '')
    sort_by = request.GET.get('sort', '-date_added')
    selected_platforms = request.GET.getlist('platform')

    if search_query:
        games_queryset = games_queryset.filter(
            Q(title__icontains=search_query) |
            Q(developer__icontains=search_query) |
            Q(publisher__icontains=search_query) |
            Q(summary__icontains=search_query)
        ).distinct()

    if selected_tier and selected_tier != 'all':
        games_queryset = games_queryset.filter(rating_tier__tier_code=selected_tier)
    if selected_flag:
        games_queryset = games_queryset.filter(flags__symbol=selected_flag).distinct()
    if requires_adjustment_filter == 'yes':
         games_queryset = games_queryset.filter(requires_adjustment=True)
    elif requires_adjustment_filter == 'no':
         games_queryset = games_queryset.filter(requires_adjustment=False)

    platform_filters = Q()
    if selected_platforms:
        platform_map = {
            'pc': 'available_pc', 'ps5': 'available_ps5', 'ps4': 'available_ps4',
            'xbx': 'available_xbox_series', 'xb1': 'available_xbox_one',
            'nsw': 'available_switch', 'and': 'available_android', 'ios': 'available_ios'
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
    games_page = paginator.get_page(page_number)

    all_tiers = RatingTier.objects.all()
    all_flags = Flag.objects.order_by('description')

    platform_list_for_template = [
        {'code': 'pc', 'name': 'PC'}, {'code': 'ps5', 'name': 'PS5'}, {'code': 'ps4', 'name': 'PS4'},
        {'code': 'xbx', 'name': 'Xbox Series'}, {'code': 'xb1', 'name': 'Xbox One'},
        {'code': 'nsw', 'name': 'Switch'}, {'code': 'and', 'name': 'Android'}, {'code': 'ios', 'name': 'iOS'},
    ]

    context = {
        'games_page': games_page, 'page_title': page_title, 'filter_description': filter_description,
        'all_tiers': all_tiers, 'all_flags': all_flags, 'search_query': search_query,
        'selected_tier': selected_tier, 'selected_flag': selected_flag,
        'requires_adjustment_filter': requires_adjustment_filter, 'sort_by': sort_by,
        'selected_platforms': selected_platforms, 'platform_list_for_template': platform_list_for_template,
    }
    return render(request, 'ratings/game_list.html', context)

# --- Game Detail View (Updated for Comments) ---
def game_detail(request, game_slug):
    game = get_object_or_404(
        Game.objects.select_related('rating_tier').prefetch_related(
            'flags', 'critic_reviews', 'comments__user', 'comments__flagged_by' # Prefetch users and flaggers
        ),
        slug=game_slug
    )
    # Get all comments, not just approved, but we'll filter in template for display logic
    all_comments = game.comments.all() # Order is handled by model Meta

    comment_form = GameCommentForm() # Initialize form for GET

    if request.method == 'POST':
        # --- Comment Submission Handling ---
        if not request.user.is_authenticated:
            messages.error(request, _("You must be logged in to post a comment."))
            return redirect(f"{reverse('login')}?next={request.path}") # Redirect to login

        # Check if user is active (not banned/deactivated)
        if not request.user.is_active:
             messages.error(request, _("Your account is currently inactive and cannot post comments."))
             context = {'game': game, 'all_comments': all_comments, 'comment_form': comment_form}
             return render(request, 'ratings/game_detail.html', context)

        comment_form = GameCommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.game = game
            new_comment.user = request.user
            new_comment.approved = True # Auto-approve
            new_comment.save()
            messages.success(request, _('Your comment has been posted.')) # Changed message
            return redirect(game.get_absolute_url() + '#comments-section') # Redirect back to the comments section
        else:
            messages.error(request, _('There was an error submitting your comment. Please check the form and CAPTCHA.'))
            # Fall through to render the page with the invalid form below

    context = {
        'game': game,
        'all_comments': all_comments, # Pass all comments
        'comment_form': comment_form,
    }
    return render(request, 'ratings/game_detail.html', context)

# --- Glossary View ---
def glossary_view(request):
    all_tiers = RatingTier.objects.all()
    context = {'all_tiers': all_tiers}
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
            # Error message includes CAPTCHA check implicitly
            messages.error(request, _("Please correct the errors below, including the CAPTCHA."))
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


# --- NEW: Delete Comment View ---
@login_required
@require_POST # Ensure this can only be accessed via POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(GameComment.objects.select_related('game'), pk=comment_id)
    game_url = comment.game.get_absolute_url() + '#comments-section' # Get URL before potential deletion

    # Check if user is staff (admin/moderator)
    if not request.user.is_staff:
        messages.error(request, _("You do not have permission to delete this comment."))
        return redirect(game_url)

    comment_content = comment.content[:30] # For message
    comment.delete()
    messages.success(request, _("Comment '%(comment_snippet)s...' deleted successfully.") % {'comment_snippet': comment_content})
    return redirect(game_url)

# --- NEW: Flag Comment View ---
@login_required
@require_POST # Ensure this can only be accessed via POST
def flag_comment(request, comment_id):
    comment = get_object_or_404(GameComment.objects.select_related('game', 'user'), pk=comment_id)
    game_url = comment.game.get_absolute_url() + '#comments-section' # Get URL

    # Prevent users from flagging their own comments
    if comment.user == request.user:
        messages.warning(request, _("You cannot flag your own comment."))
        return redirect(game_url)

    # Add user to flaggers and mark for attention
    comment.flagged_by.add(request.user)
    comment.moderator_attention_needed = True
    comment.save()

    messages.success(request, _("Comment flagged for moderator review. Thank you."))
    return redirect(game_url)

# --- NEW: Methodology View ---
def methodology_view(request):
    """Displays the MGC rating methodology page."""
    # No context needed for a static page like this yet
    context = {}
    return render(request, 'ratings/methodology.html', context)
