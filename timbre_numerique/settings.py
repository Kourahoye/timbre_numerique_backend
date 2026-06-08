import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-q(ey)@2d@04t48h!%4(ibilap)1so1l115#z93_3yt@cadq^ui'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "strawberry.django",
    'corsheaders',
    'core',
    "users.apps.UsersConfig",
    "gqlauth",
    'timbre.apps.TimbreConfig',
    'rest_framework',
]
# CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:5173",
    "https://swimmer-bullwhip-rearview.ngrok-free.dev",
    "https://sandbox-api.djomy.africa"
    
]

# APPEND_SLASH=False
USE_I18N = True
# LANGUAGE_CODE = 'fr'
USE_I18N = True
USE_L10N = True
LANGUAGES = [
    ("fr", "Français"),
    ("en", "English"),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'accept-language',   # ← ajouter explicitement
    'authorization',
    'content-type',
    'origin',
    'x-csrftoken',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',      
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',    
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'gqlauth.core.middlewares.django_jwt_middleware',
]

ROOT_URLCONF = 'timbre_numerique.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'timbre_numerique.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'timbre numerique',         # nom de la base
        'USER': 'kourahoye',       # utilisateur
        'PASSWORD': 'couratelifolia',# mot de passe
        'HOST': 'localhost',         # ou adresse IP du serveur
        'PORT': '5432',              # port par défaut
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

# LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'

AUTH_USER_MODEL = 'users.User'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

from gqlauth.settings_type import GqlAuthSettings

GQL_AUTH = GqlAuthSettings(
    LOGIN_REQUIRE_CAPTCHA=False,
    REGISTER_REQUIRE_CAPTCHA=False,
    SEND_ACTIVATION_EMAIL= False,
    ALLOW_LOGIN_NOT_VERIFIED= True,
)
JWT_AUTH = {
    'JWT_ALGORITHM': 'HS256',# 7 jours
    'JWT_AUTH_HEADER_PREFIX': 'Jwt',
}

DJOMY_CLIENT_ID = os.getenv("DJOMY_CLIENT_ID")
DJOMY_CLIENT_SECRET = os.getenv("DJOMY_CLIENT_SECRET")
DJOMY_BASE_URL = os.getenv("DJOMY_BASE_URL")

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# settings.py

PROTECTED_MEDIA_ROOT = BASE_DIR / "protected_files"

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
