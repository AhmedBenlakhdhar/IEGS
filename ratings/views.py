# ratings/views.py - FULL FILE
from django.shortcuts import render, get_object_or_404, redirect, Http404
from .models import Game, RatingTier, Flag
from articles.models import Article # Assuming articles app exists
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import SignUpForm # Import the signup form
from django.contrib.auth import login
from django.contrib import messages
from django.utils.translation import gettext_lazy as _ # Import for translation

# --- Homepage View ---
def homepage(request):
    latest_games = Game.objects.select_related('rating_tier').order_by('-date_added')[:4]
    latest_articles = Article.objects.filter(published_date__isnull=False).order_by('-published_date')[:3]
    context = {
        'latest_games': latest_games,
        'latest_articles': latest_articles,
    }
    return render(request, 'homepage.html', context)

# --- Game List View (with Filtering, Sorting, Search, Pagination) ---
def game_list(request, developer_slug=None, publisher_slug=None):
    games_queryset = Game.objects.select_related('rating_tier').prefetch_related('flags').all()
    page_title = _("Game Ratings") # Translate default title
    filter_description = None

    # Filtering by Developer/Publisher
    if developer_slug:
        games_queryset = games_queryset.filter(developer_slug=developer_slug)
        first_game = games_queryset.first()
        if first_game and first_game.developer:
            # Use f-string with translation marker if needed, or keep simple
            page_title = _("Games by %(developer_name)s") % {'developer_name': first_game.developer}
            filter_description = _("Showing games developed by <strong>%(developer_name)s</strong>.") % {'developer_name': first_game.developer}
        else:
             page_title = _("Games by Developer")
    elif publisher_slug:
        games_queryset = games_queryset.filter(publisher_slug=publisher_slug)
        first_game = games_queryset.first()
        if first_game and first_game.publisher:
            page_title = _("Games by %(publisher_name)s") % {'publisher_name': first_game.publisher}
            filter_description = _("Showing games published by <strong>%(publisher_name)s</strong>.") % {'publisher_name': first_game.publisher}
        else:
            page_title = _("Games by Publisher")

    # Get Filter/Sort Parameters
    search_query = request.GET.get('q', '')
    selected_tier = request.GET.get('tier', '')
    selected_flag = request.GET.get('flag', '')
    requires_adjustment_filter = request.GET.get('adj', '')
    sort_by = request.GET.get('sort', '-date_added')

    # Apply Search Filter
    if search_query:
        games_queryset = games_queryset.filter(
            Q(title__icontains=search_query) |
            Q(developer__icontains=search_query) |
            Q(publisher__icontains=search_query) |
            Q(summary__icontains=search_query)
        ).distinct()

    # Apply Tier Filter
    if selected_tier and selected_tier != 'all':
        games_queryset = games_queryset.filter(rating_tier__tier_code=selected_tier)

    # Apply Flag Filter
    if selected_flag:
        games_queryset = games_queryset.filter(flags__symbol=selected_flag).distinct()

    # Apply Adjustment Filter
    if requires_adjustment_filter == 'yes':
         games_queryset = games_queryset.filter(requires_adjustment=True)
    elif requires_adjustment_filter == 'no':
         games_queryset = games_queryset.filter(requires_adjustment=False)

    # Apply Sorting
    valid_sort_options = ['title', '-title', 'release_date', '-release_date', 'date_added', '-date_added']
    if sort_by in valid_sort_options:
        games_queryset = games_queryset.order_by(sort_by)
    else:
        sort_by = '-date_added'
        games_queryset = games_queryset.order_by(sort_by)

    # Pagination
    paginator = Paginator(games_queryset, 12)
    page_number = request.GET.get('page')
    try:
        games_page = paginator.page(page_number)
    except PageNotAnInteger:
        games_page = paginator.page(1)
    except EmptyPage:
        games_page = paginator.page(paginator.num_pages)

    # Data for Filters
    all_tiers = RatingTier.objects.all()
    all_flags = Flag.objects.order_by('description') # Order flags alphabetically

    context = {
        'games_page': games_page,
        'page_title': page_title,
        'filter_description': filter_description,
        'all_tiers': all_tiers,
        'all_flags': all_flags,
        'search_query': search_query,
        'selected_tier': selected_tier,
        'selected_flag': selected_flag,
        'requires_adjustment_filter': requires_adjustment_filter,
        'sort_by': sort_by,
    }
    return render(request, 'ratings/game_list.html', context)

# --- Game Detail View ---
def game_detail(request, game_slug):
    game = get_object_or_404(Game.objects.select_related('rating_tier').prefetch_related('flags'), slug=game_slug)
    context = {
        'game': game,
    }
    return render(request, 'ratings/game_detail.html', context)

# --- Glossary View ---
def glossary_view(request):
    all_tiers = RatingTier.objects.all()
    # Add more context if needed (e.g., definitions from DB)
    context = {
        'all_tiers': all_tiers,
    }
    return render(request, 'ratings/glossary.html', context)

# --- Signup View ---
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _("Registration successful! You are now logged in.")) # Translate message
            return redirect('home')
        else:
            messages.error(request, _("Please correct the errors below.")) # Translate message
    else: # GET request
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})