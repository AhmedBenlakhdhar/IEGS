# ratings/views.py
from django.shortcuts import render, get_object_or_404
from .models import Game, RatingTier
from articles.models import Article # Import Article model
from django.db.models import Q # Import Q for search later

def homepage(request):
    # Fetch, for example, the 3 latest games and 3 latest articles
    latest_games = Game.objects.select_related('rating_tier').order_by('-date_added')[:3]
    latest_articles = Article.objects.filter(published_date__isnull=False).order_by('-published_date')[:3]
    context = {
        'latest_games': latest_games,
        'latest_articles': latest_articles,
    }
    return render(request, 'homepage.html', context) # New template name

# Make sure this function definition exists exactly like this:
def game_list(request):
    """Displays a list of all games, ordered by date added."""
    # select_related fetches the ForeignKey (RatingTier) in the same query.
    # prefetch_related fetches the ManyToManyField (Flags) efficiently.
    games = Game.objects.select_related('rating_tier').prefetch_related('flags').order_by('-date_added')
    tiers = RatingTier.objects.all() # Get all tiers, maybe for filtering later
    context = {
        'games': games,
        'tiers': tiers,
        'page_title': 'Game Ratings' # Example of adding more context
    }
    return render(request, 'ratings/game_list.html', context)

# Make sure this function definition exists exactly like this:
def game_detail(request, game_slug):
    """Displays details for a specific game identified by its slug."""
    # Get the specific game or return a 404 error if not found.
    game = get_object_or_404(
        Game.objects.select_related('rating_tier').prefetch_related('flags'),
        slug=game_slug
    )
    context = {
        'game': game,
        'page_title': f"{game.title} - Rating" # Example context
    }
    return render(request, 'ratings/game_detail.html', context)

# --- Modify game_list view for search ---
def game_list(request):
    """Displays a list of all games, handles search."""
    search_query = request.GET.get('q', '') # Get search query, default to empty string
    games = Game.objects.select_related('rating_tier').prefetch_related('flags').all()

    if search_query:
        games = games.filter(
            Q(title__icontains=search_query) |
            Q(developer__icontains=search_query) |
            Q(publisher__icontains=search_query) |
            Q(summary__icontains=search_query) # Optional: search summary
        ).distinct() # Use distinct if joins cause duplicates (though less likely here)

    tiers = RatingTier.objects.all()
    context = {
        'games': games,
        'tiers': tiers,
        'search_query': search_query, # Pass query back to template
    }
    return render(request, 'ratings/game_list.html', context)

# --- game_detail view (no changes needed here for these features) ---
def game_detail(request, game_slug):
    """Displays details for a specific game."""
    game = get_object_or_404(Game.objects.select_related('rating_tier').prefetch_related('flags'), slug=game_slug)
    context = {
        'game': game,
    }
    return render(request, 'ratings/game_detail.html', context)