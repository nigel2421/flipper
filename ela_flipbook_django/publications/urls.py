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
    path('about-us/', views.about_us_view, name='about_us'),
    path('profile/', views.profile_view, name='profile'),
    path('author/<int:pk>/', views.author_detail_view, name='author_detail'),
    path('article/<slug:slug>/', views.article_detail_view, name='article_detail'),
    path('api/article/<slug:slug>/content/', views.article_content_api, name='article_content_api'),
    path('publication/<slug:slug>/', views.publication_detail_view, name='detail'),
    path('view/<slug:slug>/', views.pdf_viewer_view, name='pdf_viewer'),
    path('my-rated-articles/', views.rated_articles_view, name='rated_articles'),
    path('comment/<int:pk>/report/', views.report_comment, name='report_comment'),
    path('comment/<int:pk>/like/', views.like_comment_view, name='like_comment'),
    path('subscribe/', views.subscribe_view, name='subscribe'),
    path('contributors/', views.contributors_view, name='contributors'),
    path('submission-successful/', views.submission_successful_view, name='submission_successful'),
    path('submit/', views.submit_contribution_view, name='submit_contribution'),
    path('whatsapp-updates/', views.whatsapp_list_view, name='whatsapp_updates'),
    path('whatsapp-updates/<slug:slug>/', views.whatsapp_detail_view, name='whatsapp_detail'),
    path('track-email-open/<uuid:log_id>/', views.track_email_open, name='track_email_open'),
]
