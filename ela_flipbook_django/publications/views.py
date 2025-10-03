# publications/views.py

from django.shortcuts import render, get_object_or_404
from .models import Publication

# --- Existing Views ---
def home_view(request):
    all_publications = Publication.objects.all()
    latest_publications = Publication.objects.order_by('-uploaded_at')[:3]
    context = {
        'all_publications': all_publications,
        'latest_publications': latest_publications
    }
    return render(request, 'publications/home.html', context)

def publication_detail_view(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    context = {
        'publication': publication
    }
    return render(request, 'publications/publication_detail.html', context)

# --- NEW VIEWS ---

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

def articles_view(request):
    """
    This view also displays all publications. In the future, you could
    add a filter here for a specific category, e.g., "Article".
    """
    publications = Publication.objects.all()
    context = {
        'publications': publications
    }
    return render(request, 'publications/articles.html', context)

def contact_view(request):
    """
    This view just needs to render the contact page template.
    """
    # You can add context here later, like your email address or phone number
    return render(request, 'publications/contact.html')