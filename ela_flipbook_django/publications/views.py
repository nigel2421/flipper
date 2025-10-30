# publications/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse
from .models import Publication, Event
from allauth.account.views import SignupView # Import the original SignupView

# === CLASS-BASED VIEWS (for advanced features) ===

class CustomSignupView(SignupView):
    """
    Overrides the default signup view to capture a referral code from the URL.
    """
    def get(self, request, *args, **kwargs):
        # When a user first lands on the signup page...
        referral_code = request.GET.get('ref')
        if referral_code:
            # ...store the referral code in their session for later use.
            request.session['referral_code'] = referral_code
        # Let the original SignupView handle the rest.
        return super().get(request, *args, **kwargs)


# === FUNCTION-BASED VIEWS (for pages) ===

def home_view(request):
    """ Renders the homepage with the hero banner and publication grid. """
    all_publications = Publication.objects.all()
    latest_publications = Publication.objects.order_by('-uploaded_at')[:3]
    context = {
        'all_publications': all_publications,
        'latest_publications': latest_publications
    }
    return render(request, 'publications/home.html', context)

def magazine_view(request):
    """ Renders the magazine page with a grid of all publications. """
    publications = Publication.objects.all()
    context = {
        'publications': publications
    }
    return render(request, 'publications/magazine.html', context)

def articles_view(request):
    """ Renders the articles archive with year-based filtering. """
    selected_year = request.GET.get('year')
    year_list = Publication.objects.dates('uploaded_at', 'year', order='DESC')
    publications = Publication.objects.all()
    if selected_year and selected_year.isdigit():
        publications = publications.filter(uploaded_at__year=int(selected_year))
    context = {
        'publications': publications,
        'year_list': year_list,
        'selected_year': selected_year,
    }
    return render(request, 'publications/articles.html', context)

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

# --- THIS IS THE CORRECTED VIEW ---
@login_required
def profile_view(request):
    """ Renders the logged-in user's profile page with referral info. """
    user = request.user
    
    # Build the full, shareable referral link
    signup_url = reverse('account_signup')
    referral_link = f"{request.build_absolute_uri(signup_url)}?ref={user.profile.referral_code}"
    
    # Calculate the number of successful referrals
    referral_count = user.referrals.count()
    
    # Get the user who referred the current user, if one exists
    referrer = user.profile.referred_by
    
    # This context dictionary now includes all the necessary variables
    context = {
        'referral_link': referral_link,
        'referral_count': referral_count,
        'referrer': referrer,
    }
    return render(request, 'publications/profile.html', context)

@login_required
def publication_detail_view(request, pk):
    """ Renders the interactive flipbook viewer for a publication. """
    publication = get_object_or_404(Publication, pk=pk)
    context = {
        'publication': publication
    }
    return render(request, 'publications/publication_detail.html', context)

@login_required
def pdf_viewer_view(request, pk):
    """ Renders the simple, scrollable PDF viewer. """
    publication = get_object_or_404(Publication, pk=pk)
    context = {
        'publication': publication
    }
    return render(request, 'publications/pdf_viewer.html', context)