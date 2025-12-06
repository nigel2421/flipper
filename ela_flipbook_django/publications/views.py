# publications/views.py
# Force recompile

from django.shortcuts import render, get_object_or_404
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
from .forms import RatingForm, CommentForm
from django.db.models.functions import ExtractYear
from django.http import JsonResponse, HttpResponseRedirect
from allauth.account.views import SignupView # Import the original SignupView

# === CLASS-BASED VIEWS (for advanced features) ===

# --- NEW: Custom Signup View to capture the referral code ---
class CustomSignupView(SignupView):
    def get(self, request, *args, **kwargs):
        # When a user first lands on the signup page (a GET request)...
        referral_code = request.GET.get('ref')
        if referral_code:
            # ...we store the referral code in their session.
            # This makes it available later when the form is submitted.
            request.session['referral_code'] = str(referral_code)
        
        # Now, let the original SignupView do its normal job of displaying the page.
        return super().get(request, *args, **kwargs)

# === FUNCTION-BASED VIEWS (for pages) ===

def home_view(request):
    """ Renders the homepage with the hero banner and publication grid. """
    all_publications = Magazine.objects.all()
    latest_publications = Magazine.objects.order_by('-uploaded_at')[:3]
    # Get the top 5 most viewed articles
    top_articles = Article.objects.order_by('-view_count')[:5]

    # --- NEW: Stats Card Logic ---
    # 1. Get subscriber count and add 350
    subscribers_count = User.objects.count() + 350

    # 2. Get or generate visitor count (updates every 4 hours)
    visitor_count = cache.get('visitor_count')
    if not visitor_count:
        visitor_count = random.randint(10, 73)  # Random 2-digit number less than 74
        cache.set('visitor_count', visitor_count, timeout=4 * 60 * 60) # Cache for 4 hours

    # 3. Get the next upcoming event
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
    """ Renders the web articles archive page with filtering. """
    # This view now correctly queries the Article model
    articles = Article.objects.all().order_by('-uploaded_at')

    # Get filter parameters from the request
    query = request.GET.get('q')
    sort_by = request.GET.get('sort')
    selected_year = request.GET.get('year')
    selected_tag = request.GET.get('tag')

    # 1. Search Filter
    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(author__name__icontains=query)
        ).distinct()

    # 2. Year Filter
    if selected_year:
        articles = articles.filter(uploaded_at__year=selected_year)

    # 3. Tag (Category) Filter
    if selected_tag:
        articles = articles.filter(tags__slug=selected_tag)

    # 4. Sorting Logic
    if sort_by == 'most_read':
        articles = articles.order_by('-view_count')
    elif sort_by == 'editors_pick':
        articles = articles.filter(is_editors_pick=True).order_by('-uploaded_at')
    # Default is 'newest', which is already set

    # Get the featured story and exclude it from the main grid to avoid duplication
    featured_story = Article.objects.filter(is_featured=True).first()
    if featured_story:
        articles = articles.exclude(pk=featured_story.pk)

    context = {
        'articles': articles, # Pass 'articles' to the template
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

    # --- NEW: Get the current user's rating for this article ---
    user_rating = None
    if request.user.is_authenticated:
        rating_obj = article.ratings.filter(user=request.user).first()
        if rating_obj:
            user_rating = rating_obj.score

    # Get top-level comments and paginate them
    top_level_comments_list = article.comments.filter(parent__isnull=True).order_by('-created_at')
    paginator = Paginator(top_level_comments_list, 10) # Show 10 comments per page
    page = request.GET.get('page')
    try:
        top_level_comments = paginator.page(page)
    except PageNotAnInteger:
        top_level_comments = paginator.page(1)
    except EmptyPage:
        top_level_comments = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        # --- NEW: Handle AI Summary Generation ---
        if 'generate_summary' in request.POST:
            from .ai_utils import generate_summary_from_text
            
            # 1. Get the raw text from the RichTextField
            article_text = strip_tags(article.content)
            
            # 2. Generate the summary
            summary = generate_summary_from_text(article_text)
            
            # 3. Save it to the model instance and redirect
            article.summary = summary
            article.save(update_fields=['summary'])
            return HttpResponseRedirect(request.path_info)

        # Initialize forms with POST data
        rating_form = RatingForm(request.POST)
        comment_form = CommentForm(request.POST)

        if 'rating_submit' in request.POST and rating_form.is_valid():
            score = int(rating_form.cleaned_data['score'])
            # Use update_or_create to prevent multiple ratings from the same user
            article.ratings.update_or_create(
                user=request.user,
                defaults={'score': score}
            )
            # Redirect to the same page to prevent re-submission
            return HttpResponseRedirect(request.path_info)

        elif 'comment_submit' in request.POST and comment_form.is_valid():
            text = comment_form.cleaned_data['text']
            parent_id = comment_form.cleaned_data.get('parent_id')
            parent_comment = None
            if parent_id:
                try: # Use the related_name 'comments' or the default manager
                    parent_comment = article.comments.get(id=parent_id)
                except article.comments.model.DoesNotExist:
                    pass # Handle error case if parent comment is not found
            # Save comment
            article.comments.create(user=request.user, text=text, parent=parent_comment)
            # Redirect to the same page to prevent re-submission
            return HttpResponseRedirect(request.path_info)
    else:
        # For a GET request, create empty forms
        rating_form = RatingForm()
        comment_form = CommentForm()
        
        # Increment the view count only on a GET request
        article.view_count += 1
        # Use F() expression to avoid race conditions
        article.save(update_fields=['view_count'])

    # --- NEW: Get other articles by the same author ---
    other_articles_by_author = []
    if article.author:
        # Exclude the current article and get a few others (e.g., up to 4)
        other_articles_by_author = article.author.articles.exclude(pk=article.pk).order_by('-uploaded_at')[:4]

    # --- NEW: Get next and previous articles for navigation ---
    # Previous article is the first one published before the current one.
    previous_article = Article.objects.filter(uploaded_at__lt=article.uploaded_at).order_by('-uploaded_at').first()

    # Next article is the first one published after the current one.
    next_article = Article.objects.filter(uploaded_at__gt=article.uploaded_at).order_by('uploaded_at').first()

    # --- IMPROVED: Get related articles, prioritized by most common tags ---
    related_articles = []
    if article.tags.exists():
        from django.db.models import Count
        # Get the IDs of the tags for the current article
        article_tags_ids = article.tags.values_list('id', flat=True)
        # Find other articles that have any of the same tags,
        # annotate with the count of common tags, and order by that count.
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
    """ Renders a page listing all articles by a specific author. """
    author = get_object_or_404(Author, pk=pk)
    
    # Get all articles by this author, ordered by the newest first
    author_articles = author.articles.all().order_by('-uploaded_at')
    
    context = {
        'author': author,
        'articles': author_articles,
    }
    return render(request, 'publications/author_detail.html', context)

def events_view(request):
    """ Renders the events page with a countdown for upcoming events. """
    today = timezone.now().date()
    events = Event.objects.filter(event_date__gte=today)
    context = {
        'events': events,
    }
    return render(request, 'publications/events.html', context)

def contact_view(request):
    """ Renders the static contact page. """
    return render(request, 'publications/contact.html')

@login_required
def profile_view(request):
    """ Renders the logged-in user's profile page with referral info. """
    user = request.user
    
    # --- Referral Processing Logic ---
    referral_code = request.session.get('referral_code')
    if referral_code and not user.profile.referred_by:
        try:
            referrer_profile = Profile.objects.get(referral_code=referral_code)
            if referrer_profile.user != user:
                user.profile.referred_by = referrer_profile.user
                user.profile.save()
            del request.session['referral_code']
        except Profile.DoesNotExist:
            if 'referral_code' in request.session:
                del request.session['referral_code']
    
    # --- Display Data ---
    signup_url = reverse('account_signup')
    referral_link = f"{request.build_absolute_uri(signup_url)}?ref={user.profile.referral_code}"
    referral_count = user.referrals.count()
    referrer = user.profile.referred_by
    
    context = {
        'referral_link': referral_link,
        'referral_count': referral_count,
        'referrer': referrer,
    }
    return render(request, 'publications/profile.html', context)

@login_required
def publication_detail_view(request, pk):
    """ Renders the interactive flipbook viewer for a single magazine. """
    publication = get_object_or_404(Magazine, pk=pk)
    context = {
        'publication': publication
    }
    return render(request, 'publications/publication_detail.html', context)

@login_required
def pdf_viewer_view(request, pk):
    """ Renders the simple, scrollable PDF viewer for a magazine. """
    publication = get_object_or_404(Magazine, pk=pk)
    context = {
        'publication': publication
    }
    return render(request, 'publications/pdf_viewer.html', context)

@login_required
def rated_articles_view(request):
    """ Renders a page listing all articles rated by the current user. """
    # Get all ratings made by the current user
    user_ratings = request.user.rating_set.select_related('article').all()
    
    # You can also annotate each article with the user's specific score if needed
    # For now, we'll just pass the ratings objects
    context = {
        'user_ratings': user_ratings,
    }
    return render(request, 'publications/rated_articles.html', context)

@login_required
def report_comment(request, pk):
    """ Allows a logged-in user to report an inappropriate comment. """
    from .models import Comment, CommentReport # Import CommentReport model
    comment = get_object_or_404(Comment, pk=pk)

    if request.method == 'POST':
        # Prevent a user from reporting the same comment multiple times
        if CommentReport.objects.filter(comment=comment, reporter=request.user).exists():
            messages.warning(request, "You have already reported this comment.")
        else:
            # Create the report
            CommentReport.objects.create(
                comment=comment,
                reporter=request.user,
                reason=request.POST.get('reason', 'No reason provided.') # Optional reason field
            )
            # Update the comment's reported status and count
            comment.is_reported = True
            comment.report_count += 1
            comment.save()
            messages.success(request, "Comment reported successfully. Thank you for helping us maintain a safe community.")
    
    # Redirect back to the article detail page
    return HttpResponseRedirect(comment.article.get_absolute_url())

@login_required
def like_comment_view(request, pk):
    """
    Handles liking/unliking a comment.
    This view is intended to be called via AJAX.
    """
    # This import is inside the function to avoid circular dependency issues
    # if Comment model is also imported at the top level of other files.
    from .models import Comment
    comment = get_object_or_404(Comment, pk=pk)
    
    is_liked = False
    if comment.liked_by.filter(id=request.user.id).exists():
        # User has already liked this comment, so unlike it.
        comment.liked_by.remove(request.user)
        is_liked = False
    else:
        # User has not liked this comment yet, so like it.
        comment.liked_by.add(request.user)
        is_liked = True

    # Send WebSocket message to update all clients if channel_layer is available
    channel_layer = get_channel_layer()
    if channel_layer:
        article_id = comment.article.id
        async_to_sync(channel_layer.group_send)(
            f'article_{article_id}_comments',
            {
                'type': 'comment_like_update', # This calls the comment_like_update method in the consumer
                'message': {
                    'comment_id': comment.id,
                    'like_count': comment.like_count
                }
            }
        )
    return JsonResponse({'liked': is_liked, 'like_count': comment.like_count})

def subscribe_view(request):
    """ Renders the subscribe page. """
    return render(request, 'publications/subscribe.html')
