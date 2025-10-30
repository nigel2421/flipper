# publications/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse
from .models import Publication, Event
from allauth.account.views import SignupView

# --- Homepage View ---
def home_view(request):
    all_publications = Publication.objects.all()
    latest_publications = Publication.objects.order_by('-uploaded_at')[:3]
    context = {
        'all_publications': all_publications,
        'latest_publications': latest_publications
    }
    return render(request, 'publications/home.html', context)

# --- Publication and PDF Viewer Views (Protected) ---
@login_required
def publication_detail_view(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    context = {
        'publication': publication
    }
    return render(request, 'publications/publication_detail.html', context)

@login_required
def pdf_viewer_view(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    context = {
        'publication': publication
    }
    return render(request, 'publications/pdf_viewer.html', context)

# --- Magazine and Articles Views ---
def magazine_view(request):
    publications = Publication.objects.all()
    context = {
        'publications': publications
    }
    return render(request, 'publications/magazine.html', context)

def articles_view(request):
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

# --- Events View ---
def events_view(request):
    today = timezone.now().date()
    events = Event.objects.filter(event_date__gte=today)
    context = {
        'events': events,
    }
    return render(request, 'publications/events.html', context)

# --- Contact View ---
def contact_view(request):
    # This view is simplified and does not handle form submission for now
    return render(request, 'publications/contact.html')

# --- User Profile View (Protected) ---
@login_required
def profile_view(request):
    user = request.user
    signup_url = reverse('account_signup')
    referral_link = f"{request.build_absolute_uri(signup_url)}?ref={user.profile.referral_code}"
    referral_count = user.referrals.count()
    context = {
        'referral_link': referral_link,
        'referral_count': referral_count,
    }
    return render(request, 'publications/profile.html', context)

class CustomSignupView(SignupView):
    def get(self, request, *args, **kwargs):
        # When a user first lands on the signup page, check for a referral code
        referral_code = request.GET.get('ref')
        if referral_code:
            # Store it in the session so we can retrieve it after the POST
            request.session['referral_code'] = referral_code
        return super().get(request, *args, **kwargs)