# publications/views.py

from django.shortcuts import render, get_object_or_404, redirect
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.html import strip_tags
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from django.core.cache import cache
import random 
from .models import Magazine, Article, Event, Profile, Tag, Author # Import new models
from django.db.models import Q, Avg
from .forms import RatingForm, CommentForm, ContributorForm
from django.db.models.functions import ExtractYear
from django.http import JsonResponse, HttpResponseRedirect
from allauth.account.views import SignupView # Import the original SignupView
from django.core.mail import send_mail

# === CLASS-BASED VIEWS (for advanced features) ===

# --- NEW: Custom Signup View to capture the referral code ---
class CustomSignupView(SignupView):
    def get(self, request, *args, **kwargs):
        referral_code = request.GET.get('ref')
        if referral_code:
            request.session['referral_code'] = str(referral_code)
        return super().get(request, *args, **kwargs)

# === FUNCTION-BASED VIEWS (for pages) ===

def home_view(request):
    """ Renders the homepage with the hero banner and publication grid. """
    all_publications = Magazine.objects.all()
    latest_publications = Magazine.objects.order_by('-uploaded_at')[:3]
    top_articles = Article.objects.order_by('-view_count')[:5]

    subscribers_count = User.objects.count() + 350
    visitor_count = cache.get('visitor_count')
    if not visitor_count:
        visitor_count = random.randint(10, 73)
        cache.set('visitor_count', visitor_count, timeout=4 * 60 * 60)

    key_event = Event.objects.filter(event_date__gte=timezone.now().date()).order_by('event_date').first()

    context = {
        'all_publications': all_publications,
        'latest_publications': latest_publications,
        'top_articles': top_articles,
        'subscribers_count': subscribers_count,
        'visitor_count': visitor_count,
        'key_event': key_event,
    }
    return render(request, 'publications/home.html', context)

def magazine_view(request):
    """ Renders the magazine page with a grid of all publications. """
    publications = Magazine.objects.all()
    context = {
        'publications': publications
    }
    return render(request, 'publications/magazine.html', context)

@login_required
def articles_view(request):
    """ Renders the web articles archive page with filtering and grouping. """
    articles = Article.objects.all().order_by('-uploaded_at')

    # Get filter parameters
    query = request.GET.get('q')
    sort_by = request.GET.get('sort')
    selected_year = request.GET.get('year')
    selected_tag = request.GET.get('tag')

    # Apply filters
    if query:
        articles = articles.filter(Q(title__icontains=query) | Q(excerpt__icontains=query) | Q(author__name__icontains=query)).distinct()
    if selected_year:
        articles = articles.filter(uploaded_at__year=selected_year)
    if selected_tag:
        articles = articles.filter(tags__slug=selected_tag)

    # Apply sorting
    if sort_by == 'most_read':
        articles = articles.order_by('-view_count')
    elif sort_by == 'editors_pick':
        articles = articles.filter(is_editors_pick=True).order_by('-uploaded_at')

    # Get the featured story and exclude it from the main list
    featured_story = Article.objects.filter(is_featured=True).first()
    if featured_story:
        articles = articles.exclude(pk=featured_story.pk)

    # --- CORRECTED: Group articles by publication ---
    articles_by_publication = {}
    for article in articles:
        # Since there's no direct foreign key, we can't group by a related object.
        # Instead, we'll create a single group for all articles.
        publication_name = "All Articles"
        if publication_name not in articles_by_publication:
            articles_by_publication[publication_name] = []
        articles_by_publication[publication_name].append(article)

    context = {
        'articles_by_publication': articles_by_publication,
        'featured_story': featured_story,
        'all_tags': Tag.objects.all(),
        'year_list': Article.objects.dates('uploaded_at', 'year', order='DESC'),
        'selected_year': selected_year,
        'current_query': query,
        'current_sort': sort_by,
        'current_tag': selected_tag,
    }
    return render(request, 'publications/articles.html', context)

@login_required
def article_detail_view(request, pk):
    """ Renders a single web article page. """
    article = get_object_or_404(Article, pk=pk)

    user_rating = None
    if request.user.is_authenticated:
        rating_obj = article.ratings.filter(user=request.user).first()
        if rating_obj:
            user_rating = rating_obj.score

    top_level_comments_list = article.comments.filter(parent__isnull=True).order_by('-created_at')
    paginator = Paginator(top_level_comments_list, 10)
    page = request.GET.get('page')
    try:
        top_level_comments = paginator.page(page)
    except PageNotAnInteger:
        top_level_comments = paginator.page(1)
    except EmptyPage:
        top_level_comments = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        if 'generate_summary' in request.POST:
            from .ai_utils import generate_summary_from_text
            article_text = strip_tags(article.content)
            summary = generate_summary_from_text(article_text)
            article.summary = summary
            article.save(update_fields=['summary'])
            return HttpResponseRedirect(request.path_info)

        rating_form = RatingForm(request.POST)
        comment_form = CommentForm(request.POST)

        if 'rating_submit' in request.POST and rating_form.is_valid():
            score = int(rating_form.cleaned_data['score'])
            article.ratings.update_or_create(user=request.user, defaults={'score': score})
            return HttpResponseRedirect(request.path_info)

        elif 'comment_submit' in request.POST and comment_form.is_valid():
            text = comment_form.cleaned_data['text']
            parent_id = comment_form.cleaned_data.get('parent_id')
            parent_comment = None
            if parent_id:
                try:
                    parent_comment = article.comments.get(id=parent_id)
                except article.comments.model.DoesNotExist:
                    pass
            article.comments.create(user=request.user, text=text, parent=parent_comment)
            return HttpResponseRedirect(request.path_info)
    else:
        rating_form = RatingForm()
        comment_form = CommentForm()
        article.view_count += 1
        article.save(update_fields=['view_count'])

    other_articles_by_author = []
    if article.author:
        other_articles_by_author = article.author.articles.exclude(pk=article.pk).order_by('-uploaded_at')[:4]

    previous_article = Article.objects.filter(uploaded_at__lt=article.uploaded_at).order_by('-uploaded_at').first()
    next_article = Article.objects.filter(uploaded_at__gt=article.uploaded_at).order_by('uploaded_at').first()

    related_articles = []
    if article.tags.exists():
        from django.db.models import Count
        article_tags_ids = article.tags.values_list('id', flat=True)
        related_articles = Article.objects.filter(tags__in=article_tags_ids)\
                                          .exclude(pk=article.pk)\
                                          .annotate(common_tag_count=Count('tags'))\
                                          .order_by('-common_tag_count', '-uploaded_at')[:4]

    context = {
        'article': article,
        'rating_form': rating_form,
        'comment_form': comment_form,
        'comments': top_level_comments,
        'user_rating': user_rating,
        'other_articles_by_author': other_articles_by_author,
        'previous_article': previous_article,
        'next_article': next_article,
        'related_articles': related_articles,
    }

    return render(request, 'publications/article_detail.html', context)

def author_detail_view(request, pk):
    author = get_object_or_404(Author, pk=pk)
    author_articles = author.articles.all().order_by('-uploaded_at')
    context = {
        'author': author,
        'articles': author_articles,
    }
    return render(request, 'publications/author_detail.html', context)

def events_view(request):
    today = timezone.now().date()
    events = Event.objects.filter(event_date__gte=today)
    context = {
        'events': events,
    }
    return render(request, 'publications/events.html', context)

def contact_view(request):
    return render(request, 'publications/contact.html')

@login_required
def profile_view(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    
    referral_code = request.session.get('referral_code')
    if referral_code and not profile.referred_by:
        try:
            referrer_profile = Profile.objects.get(referral_code=referral_code)
            if referrer_profile.user != user:
                profile.referred_by = referrer_profile.user
                profile.save()
            del request.session['referral_code']
        except Profile.DoesNotExist:
            if 'referral_code' in request.session:
                del request.session['referral_code']
    
    signup_url = reverse('account_signup')
    referral_link = f"{request.build_absolute_uri(signup_url)}?ref={profile.referral_code}"
    referral_count = user.referrals.count()
    referrer = profile.referred_by
    
    context = {
        'referral_link': referral_link,
        'referral_count': referral_count,
        'referrer': referrer,
    }
    return render(request, 'publications/profile.html', context)

@login_required
def publication_detail_view(request, pk):
    publication = get_object_or_404(Magazine, pk=pk)
    context = {
        'publication': publication
    }
    return render(request, 'publications/publication_detail.html', context)

@login_required
def pdf_viewer_view(request, pk):
    publication = get_object_or_404(Magazine, pk=pk)
    context = {
        'publication': publication
    }
    return render(request, 'publications/pdf_viewer.html', context)

@login_required
def rated_articles_view(request):
    user_ratings = request.user.rating_set.select_related('article').all()
    context = {
        'user_ratings': user_ratings,
    }
    return render(request, 'publications/rated_articles.html', context)

@login_required
def report_comment(request, pk):
    from .models import Comment, CommentReport
    comment = get_object_or_404(Comment, pk=pk)

    if request.method == 'POST':
        if CommentReport.objects.filter(comment=comment, reporter=request.user).exists():
            messages.warning(request, "You have already reported this comment.")
        else:
            CommentReport.objects.create(
                comment=comment,
                reporter=request.user,
                reason=request.POST.get('reason', 'No reason provided.')
            )
            comment.is_reported = True
            comment.report_count += 1
            comment.save()
            messages.success(request, "Comment reported successfully. Thank you for helping us maintain a safe community.")
    
    return HttpResponseRedirect(comment.article.get_absolute_url())

@login_required
def like_comment_view(request, pk):
    from .models import Comment
    comment = get_object_or_404(Comment, pk=pk)
    
    is_liked = False
    if comment.liked_by.filter(id=request.user.id).exists():
        comment.liked_by.remove(request.user)
        is_liked = False
    else:
        comment.liked_by.add(request.user)
        is_liked = True

    channel_layer = get_channel_layer()
    if channel_layer:
        article_id = comment.article.id
        async_to_sync(channel_layer.group_send)(
            f'article_{article_id}_comments',
            {
                'type': 'comment_like_update',
                'message': {
                    'comment_id': comment.id,
                    'like_count': comment.like_count
                }
            }
        )
    return JsonResponse({'liked': is_liked, 'like_count': comment.like_count})

def subscribe_view(request):
    return render(request, 'publications/subscribe.html')

def contributors_view(request):
    if request.method == 'POST':
        form = ContributorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('publications:submission_successful')
    else:
        form = ContributorForm()

    return render(request, 'publications/contributors.html', {'form': form})

def submission_successful_view(request):
    return render(request, 'publications/submission_successful.html')
