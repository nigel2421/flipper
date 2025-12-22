# publications/urls.py

from django.urls import path
from . import views

app_name = 'publications'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('magazine/', views.magazine_view, name='magazine'),
    path('articles/', views.articles_view, name='articles'),
    path('events/', views.events_view, name='events'),
    path('contact/', views.contact_view, name='contact'),
    path('profile/', views.profile_view, name='profile'),
    path('author/<int:pk>/', views.author_detail_view, name='author_detail'),
    path('article/<int:pk>/', views.article_detail_view, name='article_detail'),
    path('publication/<int:pk>/', views.publication_detail_view, name='detail'),
    path('view/<int:pk>/', views.pdf_viewer_view, name='pdf_viewer'),
    path('my-rated-articles/', views.rated_articles_view, name='rated_articles'),
    path('comment/<int:pk>/report/', views.report_comment, name='report_comment'),
    path('subscribe/', views.subscribe_view, name='subscribe'),
    path('contributors/', views.contributors_view, name='contributors'),
]
