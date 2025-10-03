# publications/urls.py

from django.urls import path
from . import views

app_name = 'publications'

urlpatterns = [
    path('', views.home_view, name='home'),
    
    # New URLs for our pages
    path('magazine/', views.magazine_view, name='magazine'),
    path('articles/', views.articles_view, name='articles'),
    path('contact/', views.contact_view, name='contact'),
    
    path('publication/<int:pk>/', views.publication_detail_view, name='detail'),
]