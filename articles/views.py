# articles/views.py
from django.shortcuts import render, get_object_or_404
from .models import Article, ArticleCategory # <-- Import ArticleCategory
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext # <-- Import gettext for dynamic titles

# --- UPDATED article_list view ---
def article_list(request, category_slug=None): # <-- Add category_slug parameter
    """Displays a list of published articles, handles search and category filtering."""
    search_query = request.GET.get('q', '')
    articles_queryset = Article.objects.filter(published_date__isnull=False)
    current_category = None
    page_title = _('Blog Articles') # Default title

    # Filter by category if slug is provided
    if category_slug:
        current_category = get_object_or_404(ArticleCategory, slug=category_slug)
        articles_queryset = articles_queryset.filter(categories=current_category)
        # Dynamically set the page title using gettext for immediate translation
        page_title = gettext('Articles in: %(category_name)s') % {'category_name': current_category.name}

    # Apply search filter
    if search_query:
        articles_queryset = articles_queryset.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author_name__icontains=search_query)
        ).distinct()

    # Order the final queryset
    articles = articles_queryset.order_by('-published_date')

    # Get all categories for potential display in template (e.g., sidebar)
    all_categories = ArticleCategory.objects.all()

    context = {
        'articles': articles,
        'search_query': search_query,
        'all_categories': all_categories, # Pass categories to template
        'current_category': current_category, # Pass current category if filtering
        'page_title': page_title, # Pass dynamic page title
    }
    return render(request, 'articles/article_list.html', context)

# --- article_detail view (no changes needed unless displaying categories) ---
def article_detail(request, article_slug):
    """Displays a single article."""
    # Prefetch categories when getting the article
    article = get_object_or_404(
        Article.objects.prefetch_related('categories'), # <-- Prefetch categories
        slug=article_slug,
        published_date__isnull=False
    )
    context = {
        'article': article,
        # 'page_title': article.title, # Title already handled in base template logic
    }
    return render(request, 'articles/article_detail.html', context)