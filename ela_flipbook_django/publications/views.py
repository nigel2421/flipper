# publications/views.py

from django.shortcuts import render, get_object_or_404
from .models import Publication
from django.contrib.auth.decorators import login_required 

def home_view(request):
    """
    This view gets all publications, and also a separate list of the
    three most recent publications for the hero banner.
    """
    all_publications = Publication.objects.all()
    latest_publications = Publication.objects.order_by('-uploaded_at')[:3]
    
    context = {
        'all_publications': all_publications,
        'latest_publications': latest_publications
    }
    return render(request, 'publications/home.html', context)

@login_required
def publication_detail_view(request, pk):
    """
    This view gets a single publication by its unique ID (pk) and sends it
    to the publication_detail.html template.
    """
    publication = get_object_or_404(Publication, pk=pk)
    context = {
        'publication': publication
    }
    return render(request, 'publications/publication_detail.html', context)

@login_required
def magazine_view(request):
    """
    This view will display all publications, just like the grid on the homepage.
    We will create a separate template for it.
    """
    publications = Publication.objects.all()
    context = {
        'publications': publications
    }
    return render(request, 'publications/magazine.html', context)

@login_required
def articles_view(request):
    """
    This view now handles filtering by year and provides a list of
    distinct years for the filter dropdown.
    """
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

def pdf_viewer_view(request, pk):
    """
    This view provides a simple, scrollable, view-only display for a PDF.
    """
    publication = get_object_or_404(Publication, pk=pk)
    context = {
        'publication': publication
    }
    return render(request, 'publications/pdf_viewer.html', context)

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