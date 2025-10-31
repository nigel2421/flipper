# publications/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse
from .models import Publication, Event, Profile
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
    """ Renders the articles archive page with year-based filtering. """
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
    """ Renders the interactive flipbook viewer for a single publication. """
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