"""
Django settings for BioSaludCRUD project.
"""

from pathlib import Path
import os

# BASE_DIR apunta a la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# ⚠️ Seguridad
SECRET_KEY = 'django-insecure-8xjx5zl9u&_o%v^)!%x0fgma^(m5pt4u^fomm9ykj(-qfpl&l!'
DEBUG = True
ALLOWED_HOSTS = [
    "biosalud.cloud",
    "www.biosalud.cloud",
    "127.0.0.1",
    "localhost"
]
CSRF_TRUSTED_ORIGINS = [
    "https://biosalud.cloud",
    "https://www.biosalud.cloud"
]


# 🧩 Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',           # Admin Django
    'django.contrib.auth',            # Sistema de autenticación
    'django.contrib.contenttypes',    
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',                 # Para APIs
    'django_extensions',             # Funcionalidades extra (requiere instalación)
    'tareas',                         # Tu app principal
]

# 🧱 Middlewares (capa intermedia entre request y response)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 🌐 Configuración de URLs
ROOT_URLCONF = 'BioSaludCRUD.urls'

# 🎨 Templates y procesadores de contexto
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'tareas' / 'templates',
            BASE_DIR / 'tareas' / 'admin' / 'templates',
            BASE_DIR / 'tareas' / 'doctor' / 'templates',
            BASE_DIR / 'tareas' / 'enfermeria' / 'templates',
            BASE_DIR / 'tareas' / 'cajero' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'tareas.admin.context_processors.config_processor',
            ],
        },
    },
]

# 🚀 WSGI para producción
WSGI_APPLICATION = 'BioSaludCRUD.wsgi.application'

# 🗃️ Base de datos (sin .env)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'BioSalud_web',
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# 🔐 Validadores de contraseñas
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

# 🌍 Configuración internacional
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# 📁 Archivos estáticos (CSS, JS, imágenes)
import os

STATIC_URL = '/static/'  # ✅ Con barra al inicio

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')  # ✅ Para collectstatic

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

STATICFILES_DIRS = [
    BASE_DIR / "tareas" / "static"
]

# 🔑 Campo por defecto para claves primarias
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
