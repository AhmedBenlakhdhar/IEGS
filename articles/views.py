# articles/views.py
from django.shortcuts import render, get_object_or_404
from .models import Article
from django.db.models import Q # Import Q
from django.utils.translation import gettext_lazy as _ # Import for potential future use

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
        # Example if you wanted a dynamic title:
        # 'page_title': _('Blog Articles'),
    }
    return render(request, 'articles/article_list.html', context)

# --- article_detail view (no changes needed) ---
def article_detail(request, article_slug):
    """Displays a single article."""
    article = get_object_or_404(Article, slug=article_slug, published_date__isnull=False)
    context = {
        'article': article,
        # Example:
        # 'page_title': article.title, # Title comes from model, already marked there
    }
    return render(request, 'articles/article_detail.html', context)