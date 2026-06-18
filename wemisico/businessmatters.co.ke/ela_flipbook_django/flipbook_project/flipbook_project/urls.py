# flipbook_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from publications.views import CustomSignupView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Custom signup view — captures referral codes and shows the real sign-up form.
    # IMPORTANT: this must come BEFORE the generic allauth include below so Django
    # matches it first and does not fall through to allauth's default signup view.
    path('accounts/signup/', CustomSignupView.as_view(), name='account_signup'),

    # All other allauth URLs (login, logout, password reset, social auth, etc.)
    path('accounts/', include('allauth.urls')),

    # App pages
    path('', include('publications.urls')),
]

# Serve uploaded media files locally during development only.
# In production the web server (LiteSpeed/Apache) handles this directly.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)