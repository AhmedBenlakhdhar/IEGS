# articles/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Article, ArticleCategory, ArticleComment
from .forms import ArticleCommentForm
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpResponseForbidden

# --- UPDATED article_list view ---
def article_list(request, category_slug=None):
    """Displays a list of published articles, handles search and category filtering."""
    search_query = request.GET.get('q', '')
    # REMOVED .select_related('author') HERE
    articles_queryset = Article.objects.filter(published_date__isnull=False)
    current_category = None
    page_title = _('Blog Articles')

    if category_slug:
        current_category = get_object_or_404(ArticleCategory, slug=category_slug)
        articles_queryset = articles_queryset.filter(categories=current_category)
        page_title = gettext('Articles in: %(category_name)s') % {'category_name': current_category.name}

    if search_query:
        articles_queryset = articles_queryset.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author_name__icontains=search_query)
        ).distinct()

    # Prefetch categories AFTER filtering is done for efficiency
    articles = articles_queryset.prefetch_related('categories').order_by('-published_date')

    all_categories = ArticleCategory.objects.all()

    context = {
        'articles': articles,
        'search_query': search_query,
        'all_categories': all_categories,
        'current_category': current_category,
        'page_title': page_title,
    }
    return render(request, 'articles/article_list.html', context)


# --- article_detail view (Keep as is) ---
def article_detail(request, article_slug):
    article = get_object_or_404(
        Article.objects.prefetch_related('categories', 'comments__user', 'comments__flagged_by'),
        slug=article_slug,
        published_date__isnull=False
    )
    all_comments = article.comments.all()
    comment_form = ArticleCommentForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, _("You must be logged in to post a comment."))
            login_url = reverse('login')
            return redirect(f'{login_url}?next={request.path}')
        if not request.user.is_active:
            messages.error(request, _("Your account is currently inactive and cannot post comments."), extra_tags='comment_error')
            context = {'article': article, 'all_comments': all_comments, 'comment_form': comment_form}
            return render(request, 'articles/article_detail.html', context)

        comment_form = ArticleCommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.article = article
            new_comment.user = request.user
            new_comment.approved = True
            new_comment.save()
            messages.success(request, _('Your comment has been posted.'), extra_tags='comment_success')
            return redirect(article.get_absolute_url() + '#comments-section')
        else:
            messages.error(request, _('There was an error submitting your comment. Please check the form and CAPTCHA.'), extra_tags='comment_error')

    context = {
        'article': article,
        'all_comments': all_comments,
        'comment_form': comment_form,
    }
    return render(request, 'articles/article_detail.html', context)

# --- Delete/Flag Article Comment Views (Keep as is) ---
@login_required
@require_POST
def delete_article_comment(request, comment_id):
    comment = get_object_or_404(ArticleComment.objects.select_related('article'), pk=comment_id)
    article_url = comment.article.get_absolute_url() + '#comments-section'
    if not request.user.is_staff:
        messages.error(request, _("You do not have permission to delete this comment."))
        return redirect(article_url)
    comment_content = comment.content[:30]
    comment.delete()
    messages.success(request, _("Comment '%(comment_snippet)s...' deleted successfully.") % {'comment_snippet': comment_content})
    return redirect(article_url)

@login_required
@require_POST
def flag_article_comment(request, comment_id):
    comment = get_object_or_404(ArticleComment.objects.select_related('article', 'user'), pk=comment_id)
    article_url = comment.article.get_absolute_url() + '#comments-section'
    if comment.user == request.user:
        messages.warning(request, _("You cannot flag your own comment."))
        return redirect(article_url)
    if comment.flagged_by.filter(pk=request.user.pk).exists():
        messages.info(request, _("You have already flagged this comment."))
        return redirect(article_url)
    comment.flagged_by.add(request.user)
    comment.moderator_attention_needed = True
    comment.save()
    messages.success(request, _("Comment flagged for moderator review. Thank you."))
    return redirect(article_url)