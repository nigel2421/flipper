"""
Django settings for flipbook_project project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-p)$_lf*$b=h2x(l9cv^r8yo(662fa^1=nbnfs+fe8(iw-x^c+&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False # Set to False for production!

ALLOWED_HOSTS = [ 
    'press.businessmatters.co.ke',
    'businessmatters.co.ke',
    '127.0.0.1',
    'localhost',
    'www.businessmatters.co.ke', # <-- Added for completeness
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',        # <-- CORE: Must be before allauth
    'publications',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    # Core Django Middleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Allauth & Custom Middleware
    'allauth.account.middleware.AccountMiddleware',
    'publications.middleware.ReferralMiddleware',
]

ROOT_URLCONF = 'flipbook_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                 'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'flipbook_project.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# --- Static and Media File Configuration ---
STATIC_URL = 'flipper/ela_flipbook_django/publications/static/'
MEDIA_URL = 'flipper/ela_flipbook_django/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
X_FRAME_OPTIONS = 'SAMEORIGIN'


# --- AUTHENTICATION & ALLAUTH SETTINGS ---
SITE_ID = 1 # The ID of the primary site record in django_site table

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Allauth core settings
ACCOUNT_EMAIL_VERIFICATION = 'none' 
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_FORMS = { 'signup': 'publications.forms.CustomSignupForm', }


# Redirects and URLs
LOGIN_URL = '/accounts/login/' 
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


# Allauth Social Settings
SOCIALACCOUNT_LOGIN_ON_SEPARATE_URLS = True
SESSION_COOKIE_AGE = 25920000 # 30 days


# --- EMAIL CONFIGURATION ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = (EMAIL_PORT == 587)
EMAIL_USE_SSL = (EMAIL_PORT == 465)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# === PRODUCTION/SECURITY CONFIGURATION ===

if DEBUG:
    # Local Development: No SSL, no strong headers
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"
else:
    # Production: Enforce SSL/HTTPS and proxy headers
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
    
    # REQUIRED FOR PROXY/LOAD BALANCER (like LiteSpeed/cPanel)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Enforce security headers/cookies
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True