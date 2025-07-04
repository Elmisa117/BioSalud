"""
Django settings for BioSaludCRUD project.
"""

from pathlib import Path
import os

# BASE_DIR apunta a la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# ⚠️ Seguridad
SECRET_KEY = 'clave_super_secreta_123'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# 🧩 Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_extensions',
    'tareas',
]

# 🧱 Middlewares
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

# 🎨 Templates y contexto
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

# 🚀 WSGI
WSGI_APPLICATION = 'BioSaludCRUD.wsgi.application'

# 🗃️ Base de datos (sin .env)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'BioSalud',
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# 🔐 Validadores de contraseña
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

# 🌍 Internacionalización
LANGUAGE_CODE = 'es-bo'
TIME_ZONE = 'America/La_Paz'
USE_I18N = True
USE_TZ = True

# 📁 Archivos estáticos
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "tareas" / "static"
]

# 🔑 Clave primaria automática
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 🔐 Configuración biométrica (opcional)
BIOMETRIC_CONFIG = {
    'ENCRYPTION_KEY': 'clavebiometrica123',
}
