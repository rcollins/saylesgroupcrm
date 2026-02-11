import os
import warnings
from pathlib import Path

import dj_database_url

# Suppress WhiteNoise warning when STATIC_ROOT is missing (e.g. on Vercel until staticfiles/ is committed).
warnings.filterwarnings('ignore', message='No directory at')
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root (parent of the directory containing manage.py)
load_dotenv(BASE_DIR.parent / '.env')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Must be provided via environment (.env). No hard-coded fallback.
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required (set it in your .env file).")

# SECURITY WARNING: don't run with debug turned on in production!
# In development, leave DEBUG unset or set DEBUG=True so media/static are served; set DEBUG=False in production (e.g. Vercel).
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('1', 'true', 'yes')

# In production, set ALLOWED_HOSTS via env (comma-separated) to avoid accepting any host.
# Do not use '*' in production (enables host header attacks).
_allowed = os.environ.get('ALLOWED_HOSTS', '').strip()
if _allowed:
    ALLOWED_HOSTS = [h.strip() for h in _allowed.split(',') if h.strip()]
else:
    ALLOWED_HOSTS = [
        '.vercel.app',
        '.now.sh',
        'localhost',
        '127.0.0.1',
        'saylesgroupcrm.vercel.app',
    ]


# CSRF settings for Vercel
CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'https://*.now.sh',
    'https://saylesgroupcrm-git-main-robert-collins-jrs-projects.vercel.app/',
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crm',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'recrmapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'crm.context_processors.app_settings',
                'crm.context_processors.choice_labels',
            ],
        },
    },
]

WSGI_APPLICATION = 'recrmapp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600),
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/
# On Vercel: set Build Command to "python manage.py collectstatic --noinput" so staticfiles/ exists in the deployment.

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (user uploads, e.g. property photos)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Use S3-compatible storage in production (e.g. Vercel) so uploads don't hit read-only filesystem.
# Set AWS_STORAGE_BUCKET_NAME (and credentials) in Vercel env; works with AWS S3 or Cloudflare R2.
# Only use S3 when the bucket is set AND django-storages is installed (so local dev works without it).
def _use_s3_storage():
    if not os.environ.get('AWS_STORAGE_BUCKET_NAME'):
        return False
    try:
        import storages.backends.s3  # noqa: F401
        return True
    except ImportError:
        return False


AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
if AWS_STORAGE_BUCKET_NAME and _use_s3_storage():
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3.S3Storage',
            'OPTIONS': {
                'bucket_name': AWS_STORAGE_BUCKET_NAME,
                'location': os.environ.get('AWS_S3_LOCATION', 'media'),
                'region_name': os.environ.get('AWS_S3_REGION_NAME') or None,
                'default_acl': 'public-read',
                'querystring_auth': False,
                #'custom_domain': os.environ.get('AWS_S3_CUSTOM_DOMAIN') or None,
                #'endpoint_url': os.environ.get('AWS_S3_ENDPOINT_URL') or None,
            },
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    }
    if os.environ.get('AWS_S3_CUSTOM_DOMAIN'):
        MEDIA_URL = f"https://{os.environ['AWS_S3_CUSTOM_DOMAIN']}/"
else:
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
            'OPTIONS': {'location': MEDIA_ROOT, 'base_url': MEDIA_URL},
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    }

# Authentication
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Email (Anymail + Resend)
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
if RESEND_API_KEY:
    EMAIL_BACKEND = 'anymail.backends.resend.EmailBackend'
    ANYMAIL = {
        'RESEND_API_KEY': RESEND_API_KEY,
    }
    # From address: use a verified domain in Resend, or Resend's sandbox for testing
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'The Sayles Group CRM <onboarding@resend.dev>')
    SERVER_EMAIL = DEFAULT_FROM_EMAIL
else:
    # No API key: use console backend so send_mail() doesn't fail (e.g. in dev)
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'robert@saylesgrouphomes.com')

# Security hardening (recommended for production)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = False  # False so JS can read for AJAX; use SameSite
CSRF_COOKIE_SAMESITE = 'Lax'
