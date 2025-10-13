# publications/views.py

from django.shortcuts import render, get_object_or_404
from .models import Publication

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

def contact_view(request):
    """
    This view just needs to render the contact page template.
    """
    return render(request, 'publications/contact.html')