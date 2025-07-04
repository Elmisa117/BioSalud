"""
Django settings for BioSaludCRUD project.
"""

from pathlib import Path
<<<<<<< HEAD
import os
=======
>>>>>>> 1093de99b066a9f4b5e91d4eb888763403e01199

# BASE_DIR apunta a la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# ⚠️ Seguridad
<<<<<<< HEAD
SECRET_KEY = 'clave_super_secreta_123'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
=======
SECRET_KEY = 'django-insecure-8xjx5zl9u&_o%v^)!%x0fgma^(m5pt4u^fomm9ykj(-qfpl&l!'
DEBUG = True
<<<<<<< HEAD
ALLOWED_HOSTS = ['141.95.161.224', 'localhost', '127.0.0.1']
>>>>>>> 1093de99b066a9f4b5e91d4eb888763403e01199
=======
ALLOWED_HOSTS = ['141.95.161.224', 'biosalud.cloud', 'www.biosalud.cloud']
>>>>>>> 7261256c11e8861d0d27a2b76ed8274c27c2c4e4

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

<<<<<<< HEAD
# 🗃️ Base de datos (sin .env)
=======
# 🗃️ Base de datos PostgreSQL
>>>>>>> 1093de99b066a9f4b5e91d4eb888763403e01199
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

<<<<<<< HEAD
# 🌍 Internacionalización
LANGUAGE_CODE = 'es-bo'
TIME_ZONE = 'America/La_Paz'
=======
# 🌍 Configuración internacional
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
>>>>>>> 1093de99b066a9f4b5e91d4eb888763403e01199
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
<<<<<<< HEAD

# 🔐 Configuración biométrica (opcional)
BIOMETRIC_CONFIG = {
    'ENCRYPTION_KEY': 'clavebiometrica123',
}
=======
>>>>>>> 1093de99b066a9f4b5e91d4eb888763403e01199
