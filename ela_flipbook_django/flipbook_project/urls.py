# flipbook_project/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    path("ckeditor5/", include('django_ckeditor_5.urls')),

    # 1. Sign-Up is immediately redirected to the Google login flow.
    path("accounts/signup/",
         RedirectView.as_view(url='/accounts/google/login/', permanent=False, query_string=True),
         name="account_signup"
    ),

    # 2. All other allauth URLs
    path('accounts/', include('allauth.urls')),

    path('', include('publications.urls')),

    # Force serve media files in production (shared hosting fix)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

# This is for serving files in development and should be appended at the end.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
