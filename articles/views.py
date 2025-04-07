# articles/views.py
from django.shortcuts import render, get_object_or_404, redirect # Add redirect
from django.urls import reverse # Add reverse
from .models import Article, ArticleCategory, ArticleComment # <-- Import ArticleComment
from .forms import ArticleCommentForm # <-- Import ArticleCommentForm
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from django.contrib.auth.decorators import login_required # <-- Import login_required
from django.views.decorators.http import require_POST # <-- Import require_POST
from django.contrib import messages # <-- Import messages
from django.http import HttpResponseForbidden # <-- Import HttpResponseForbidden

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

# --- UPDATED article_detail view ---
def article_detail(request, article_slug):
    """Displays a single article and handles comment submission."""
    article = get_object_or_404(
        Article.objects.prefetch_related('categories', 'comments__user', 'comments__flagged_by'), # Prefetch comments too
        slug=article_slug,
        published_date__isnull=False
    )
    all_comments = article.comments.all() # Get all comments for logic, filter in template
    comment_form = ArticleCommentForm() # Initialize form for GET

    if request.method == 'POST':
        # --- Comment Submission Handling ---
        if not request.user.is_authenticated:
            messages.error(request, _("You must be logged in to post a comment."))
            # Redirect to login, adding the current article path as the 'next' parameter
            login_url = reverse('login')
            return redirect(f'{login_url}?next={request.path}')

        # Check if user is active
        if not request.user.is_active:
            messages.error(request, _("Your account is currently inactive and cannot post comments."), extra_tags='comment_error') # Add tag
            # Re-render the page with the form and error
            context = {'article': article, 'all_comments': all_comments, 'comment_form': comment_form}
            return render(request, 'articles/article_detail.html', context)

        comment_form = ArticleCommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.article = article
            new_comment.user = request.user
            new_comment.approved = True # Auto-approve
            new_comment.save()
            messages.success(request, _('Your comment has been posted.'), extra_tags='comment_success') # Add tag
            # Redirect back to the same article detail page, focusing on the comments section
            return redirect(article.get_absolute_url() + '#comments-section')
        else:
            # Add a generic error message if the form is invalid (specific errors are shown by the fields)
            messages.error(request, _('There was an error submitting your comment. Please check the form and CAPTCHA.'), extra_tags='comment_error') # Add tag
            # Fall through to render the page with the invalid form below

    context = {
        'article': article,
        'all_comments': all_comments, # Pass all comments to the template
        'comment_form': comment_form, # Pass the form (potentially invalid)
    }
    return render(request, 'articles/article_detail.html', context)

# --- NEW: Delete Article Comment View ---
@login_required
@require_POST # Ensure this can only be accessed via POST
def delete_article_comment(request, comment_id):
    comment = get_object_or_404(ArticleComment.objects.select_related('article'), pk=comment_id)
    article_url = comment.article.get_absolute_url() + '#comments-section'

    # Only allow staff to delete comments
    if not request.user.is_staff:
        messages.error(request, _("You do not have permission to delete this comment."))
        return redirect(article_url)

    comment_content = comment.content[:30] # For message
    comment.delete()
    messages.success(request, _("Comment '%(comment_snippet)s...' deleted successfully.") % {'comment_snippet': comment_content})
    return redirect(article_url)

# --- NEW: Flag Article Comment View ---
@login_required
@require_POST # Ensure this can only be accessed via POST
def flag_article_comment(request, comment_id):
    comment = get_object_or_404(ArticleComment.objects.select_related('article', 'user'), pk=comment_id)
    article_url = comment.article.get_absolute_url() + '#comments-section'

    # Prevent users from flagging their own comments or if already flagged
    if comment.user == request.user:
        messages.warning(request, _("You cannot flag your own comment."))
        return redirect(article_url)
    if comment.flagged_by.filter(pk=request.user.pk).exists():
        messages.info(request, _("You have already flagged this comment."))
        return redirect(article_url)

    # Add user to flaggers and mark for attention
    comment.flagged_by.add(request.user)
    comment.moderator_attention_needed = True
    comment.save()

    messages.success(request, _("Comment flagged for moderator review. Thank you."))
    return redirect(article_url)
