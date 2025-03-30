# articles/views.py
from django.shortcuts import render, get_object_or_404
from .models import Article
from django.db.models import Q # Import Q

def article_list(request):
    """Displays a list of all published articles, handles search."""
    search_query = request.GET.get('q', '') # Get search query
    articles = Article.objects.filter(published_date__isnull=False).order_by('-published_date')

    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author_name__icontains=search_query)
        ).distinct()

    context = {
        'articles': articles,
        'search_query': search_query, # Pass query back
    }
    return render(request, 'articles/article_list.html', context)

# --- article_detail view (no changes needed) ---
def article_detail(request, article_slug):
    """Displays a single article."""
    article = get_object_or_404(Article, slug=article_slug, published_date__isnull=False)
    context = {
        'article': article,
    }
    return render(request, 'articles/article_detail.html', context)