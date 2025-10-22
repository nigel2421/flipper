# publications/urls.py

from django.urls import path
from . import views
from django.contrib import admin
from django.urls import path, include


app_name = 'publications'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('magazine/', views.magazine_view, name='magazine'),
    path('articles/', views.articles_view, name='articles'),
    path('contact/', views.contact_view, name='contact'),

     path('admin/', admin.site.urls),
    
    # Add allauth's URLs under the 'accounts/' path
    path('accounts/', include('allauth.urls')),

    
    path('', include('publications.urls')),
    
    
    # This is the flipbook viewer
    path('publication/<int:pk>/', views.publication_detail_view, name='detail'),
    
    # This is the NEW simple, scrollable viewer
    path('view/<int:pk>/', views.pdf_viewer_view, name='pdf_viewer'),
]