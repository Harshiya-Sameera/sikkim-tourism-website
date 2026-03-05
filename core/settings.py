import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

if os.name == "nt":

    OSGEO4W_ROOT = r"C:\QGIS 3.44.7"

    QGIS_BIN = os.path.join(OSGEO4W_ROOT, "bin")
    GDAL_BIN = os.path.join(OSGEO4W_ROOT, "apps", "gdal", "bin")
    QGIS_APP_BIN = os.path.join(OSGEO4W_ROOT, "apps", "qgis", "bin")
    QT_BIN = os.path.join(OSGEO4W_ROOT, "apps", "Qt5", "bin")

    os.environ["PATH"] = (
        QGIS_BIN + ";" +
        GDAL_BIN + ";" +
        QGIS_APP_BIN + ";" +
        QT_BIN + ";" +
        os.environ.get("PATH", "")
    )

    os.environ["GDAL_DATA"] = os.path.join(OSGEO4W_ROOT, "apps", "gdal", "share", "gdal")
    os.environ["PROJ_LIB"] = os.path.join(OSGEO4W_ROOT, "share", "proj")

    GDAL_LIBRARY_PATH = os.path.join(QGIS_BIN, "gdal312.dll")
    GEOS_LIBRARY_PATH = os.path.join(QGIS_BIN, "geos_c.dll")
    SPATIALITE_LIBRARY_PATH = os.path.join(QGIS_BIN, "mod_spatialite.dll")

    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(QGIS_BIN)
        os.add_dll_directory(GDAL_BIN)
        os.add_dll_directory(QGIS_APP_BIN)
        os.add_dll_directory(QT_BIN)

        
load_dotenv()

AI_API_KEY = os.getenv("AI_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Only needed for production, but harmless in dev
STATIC_ROOT = BASE_DIR / 'staticfiles'

# --- SECURITY SETTINGS ---
SECRET_KEY = 'django-insecure-uax7k!b(mx03n%6#qj&8#%_$yenh*3rn&6fz88o!n78@ke%q^5'

DEBUG = True

ALLOWED_HOSTS = ['*']

# Add this near the top or bottom of settings.py
AUTH_USER_MODEL = 'accounts.User'

# Corrected INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Fixed: removed .models.Site
    
    # Third Party Apps
    'rest_framework',
    
    # Local Apps
    'portal',  
    'accounts',
    'chatbot',
    'tourism',
    'itinerary',
    'adminpanel',
    'leaflet',
]

SITE_ID = 1

LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (27.3314, 88.6138), # Default to Gangtok, Sikkim
    'DEFAULT_ZOOM': 10,
    'MIN_ZOOM': 5,
    'MAX_ZOOM': 18,
    'TILES': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    'ATTRIBUTION_PREFIX': 'Sikkim Tourism AI Platform',
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    # LocaleMiddleware MUST be here
    'django.middleware.locale.LocaleMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 2. Persistence settings
LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 31536000 # 1 year persistence

ROOT_URLCONF = 'core.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
           'context_processors': [
    'django.template.context_processors.debug',
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.template.context_processors.i18n',

    'portal.context_processors.base_template',
],

        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# --- DATABASE ---
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.spatialite",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

SPATIALITE_LIBRARY_PATH = r"C:\QGIS 3.44.7\bin\mod_spatialite.dll"
# --- PASSWORD VALIDATION ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- INTERNATIONALIZATION & LOCALIZATION ---
LANGUAGE_CODE = 'en'
TIME_ZONE = 'Asia/Kolkata' 
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Supported Languages
LANGUAGES = [
    ('en', _('English')),
    ('hi', _('Hindi')),
    ('te', _('Telugu')),
]

# Path where .po and .mo files will be stored
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# --- STATIC AND MEDIA FILES ---
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- EMAIL CONFIGURATION (SMTP) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'harisaiparasa@gmail.com'
EMAIL_HOST_PASSWORD = 'khgpmkjfacdsqchk'

# --- MISC ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# AI_API_KEY = "AIzaSyA1XC2smURg6PX8LVboTssMV2zYPvILKCk"
OPENWEATHERMAP_API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY", "")