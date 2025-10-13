# publications/urls.py

from django.urls import path
from . import views

app_name = 'publications'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('magazine/', views.magazine_view, name='magazine'),
    path('articles/', views.articles_view, name='articles'),
    path('contact/', views.contact_view, name='contact'),
    
    # This is the flipbook viewer
    path('publication/<int:pk>/', views.publication_detail_view, name='detail'),
    
    # This is the NEW simple, scrollable viewer
    path('view/<int:pk>/', views.pdf_viewer_view, name='pdf_viewer'),
]