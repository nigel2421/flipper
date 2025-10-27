# publications/views.py

<<<<<<< HEAD
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Publication, Event
=======
from django.shortcuts import render, get_object_or_404
from .models import Publication
from django.contrib.auth.decorators import login_required 
>>>>>>> a5c18e4747cac8705105c910b405787f217e22c9

# --- Homepage View ---
def home_view(request):
    all_publications = Publication.objects.all()
    latest_publications = Publication.objects.order_by('-uploaded_at')[:3]
    context = {
        'all_publications': all_publications,
        'latest_publications': latest_publications
    }
    return render(request, 'publications/home.html', context)

<<<<<<< HEAD
# --- Publication and PDF Viewer Views (Protected) ---
=======
>>>>>>> a5c18e4747cac8705105c910b405787f217e22c9
@login_required
def publication_detail_view(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    context = {
        'publication': publication
    }
    return render(request, 'publications/publication_detail.html', context)

@login_required
<<<<<<< HEAD
def pdf_viewer_view(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    context = {
        'publication': publication
    }
    return render(request, 'publications/pdf_viewer.html', context)

# --- Magazine and Articles Views ---
=======
>>>>>>> a5c18e4747cac8705105c910b405787f217e22c9
def magazine_view(request):
    publications = Publication.objects.all()
    context = {
        'publications': publications
    }
    return render(request, 'publications/magazine.html', context)

@login_required
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

<<<<<<< HEAD
# --- Contact View ---
def contact_view(request):
    # This view is simplified and does not handle form submission for now
    return render(request, 'publications/contact.html')

# --- User Profile View (Protected) ---
@login_required
def profile_view(request):
    user = request.user
    from django.urls import reverse
    signup_url = reverse('account_signup')
    referral_link = f"{request.build_absolute_uri(signup_url)}?ref={user.profile.referral_code}"
    referral_count = user.referrals.count()
    context = {
        'referral_link': referral_link,
        'referral_count': referral_count,
    }
    return render(request, 'publications/profile.html', context)
=======
# publications/views.py

# ... (imports) ...

def contact_view(request):
    if request.method == 'POST':
        # ... (get form data) ...
        
        try:
            send_mail(
                subject,
                email_message,
                'info@businessmatters.com',  # From: Your email address
                ['info@businessmatters.com'],  # To: The inbox you want to receive messages in
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully! Thank you.')
        except Exception as e:
            messages.error(request, 'Sorry, there was an error sending your message. Please try again later.')

        return redirect('publications:contact')

    return render(request, 'publications/contact.html')

# --- NEW PROFILE VIEW ---
@login_required
def profile_view(request):
    """
    Displays the logged-in user's profile information.
    """
    # The user object is automatically available in the request
    return render(request, 'publications/profile.html')
>>>>>>> a5c18e4747cac8705105c910b405787f217e22c9
