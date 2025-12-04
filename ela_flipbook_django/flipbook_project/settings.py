"""
Django settings for flipbook_project project.
"""

from pathlib import Path
import os
import dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
dotenv.load_dotenv(os.path.join(BASE_DIR, '.env'))


# Quick-start development settings - unsuitable for production
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-p)$_lf*$b=h2x(l9cv^r8yo(662fa^1=nbnfs+fe8(iw-x^c+&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True # Set to False for production!

ALLOWED_HOSTS = [ 
    'press.businessmatters.co.ke',
    'businessmatters.co.ke',
    '127.0.0.1',
    'localhost',
    'www.businessmatters.co.ke',
    # Add the development server host
    '8000-firebase-flippergit-1764678684466.cluster-cbeiita7rbe7iuwhvjs5zww2i4.cloudworkstations.dev',
]

# Trust the development server origin for CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://8000-firebase-flippergit-1764678684466.cluster-cbeiita7rbe7iuwhvjs5zww2i4.cloudworkstations.dev',
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
    'django_ckeditor_5',
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


# --- GOOGLE AI API CONFIGURATION ---
# Store your key in an environment variable for security.
# Example: GOOGLE_API_KEY='your-secret-api-key'
GOOGLE_API_KEY = os.environ.get('GEMINI_API_KEY')


# --- Static and Media File Configuration ---
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
X_FRAME_OPTIONS = 'SAMEORIGIN'


STATIC_ROOT = BASE_DIR / 'staticfiles_collected'

# --- AUTHENTICATION & ALLAUTH SETTINGS ---
SITE_ID = 1 # The ID of the primary site record in django_site table

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Allauth core settings
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_LOGIN_METHODS = ['email']  # Use the new setting name (plural) and provide it as a list
ACCOUNT_SIGNUP_FIELDS = ['email'] # Use the new setting name
ACCOUNT_USER_MODEL_USERNAME_FIELD = None # Explicitly state no username is used
ACCOUNT_FORMS = { 'signup': 'publications.forms.CustomSignupForm', }


# Redirects and URLs
LOGIN_URL = '/accounts/login/' 
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


# Allauth Social Settings
SOCIALACCOUNT_LOGIN_ON_SEPARATE_URLS = True
SESSION_COOKIE_AGE = 25920000 # 30 days

# My settings
SOCIALACCOUNT_ADAPTER = 'publications.adapter.CustomSocialAccountAdapter'

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

if not DEBUG:
    # Production: Enforce SSL/HTTPS and proxy headers
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
    
    # REQUIRED FOR PROXY/LOAD BALANCER (like LiteSpeed/cPanel)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Enforce security headers/cookies
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
else:
    # Local Development: No SSL, no strong headers
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"

# --- CKEDITOR CONFIGURATION ---
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|', 
            'bold', 'italic', 'underline', 'strikethrough', 'link', 'bulletedList', 'numberedList', 'blockquote', '|',
            'fontfamily', 'fontsize', 'fontColor', 'fontBackgroundColor', '|',
            'alignment', '|',
            'outdent', 'indent', '|',
            'uploadImage', 'insertTable', 'undo', 'redo',
        ],
        'image': {
            'toolbar': ['imageTextAlternative', 'imageTitle', '|', 'imageStyle:alignLeft', 'imageStyle:full', 'imageStyle:alignRight'],
            'styles': ['full', 'alignLeft', 'alignRight']
        },
        'theme': 'lark',
        'height': 300,
        'language': 'en',
    },
}

CKEDITOR_5_CUSTOM_CSS = 'publications/css/ckeditor-fix.css'
