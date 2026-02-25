from pathlib import Path
import os

# --------------------------------
# Base paths
# --------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --------------------------------
# Seguridad
# --------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "insecure-dev-key")

DEBUG = False

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

# --------------------------------
# Auditoria
# --------------------------------
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# --------------------------------
# Apps
# --------------------------------
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django_filters',
    # Third party apps 
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',  # Para logout
    'corsheaders',
    # Swagger
    'drf_spectacular',
    # Nuestras apps 
    'apps.core',
    'apps.users',
    'apps.auth',
]

# --------------------------------
# Middleware
# --------------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --------------------------------
# URLs / WSGI
# --------------------------------
ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"

# --------------------------------
# Templates
# --------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# --------------------------------
# Database (PostgreSQL – Docker)
# --------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.getenv("DB_HOST", "postgres"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "CONN_MAX_AGE": 60,
    }
}

# --------------------------------
# Password validation
# --------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]
AUTH_USER_MODEL = 'auth.User'  # User nativo de Django

# ==============================================================================
# REST FRAMEWORK 
# ==============================================================================
REST_FRAMEWORK = {
    # Autenticación por defecto: JWT
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    
    # Permisos por defecto: Requiere autenticación
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    
    # Paginación por defecto
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    
    # ← AGREGAR ESTO PARA SWAGGER
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    
    # Formato de fecha/hora
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    
    # Filtros, búsqueda, ordenamiento
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
     'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',     # Usuarios no autenticados
        'user': '1000/hour',    # Usuarios autenticados
        'login': '5/minute',    # Login específico
    },
    # Manejo de excepciones personalizado (opcional)
    # 'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
    
    # Throttling (rate limiting) - opcional, descomentar si necesitas
    # 'DEFAULT_THROTTLE_CLASSES': [
    #     'rest_framework.throttling.AnonRateThrottle',
    #     'rest_framework.throttling.UserRateThrottle',
    # ],
    # 'DEFAULT_THROTTLE_RATES': {
    #     'anon': '100/hour',
    #     'user': '1000/hour',
    # },
}

# ==============================================================================
# JWT CONFIGURATION 
# ==============================================================================
from datetime import timedelta

SIMPLE_JWT = {
    # Duración del access token (corto por seguridad)
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=2),  # 1 hora
    
    # Duración del refresh token (largo para UX)
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=5),#days=1),  # 1 día
    
    # Rotar refresh token al usarlo (más seguro)
    'ROTATE_REFRESH_TOKENS': True,
    
    # Blacklist tokens viejos al rotar
    'BLACKLIST_AFTER_ROTATION': True,
    
    # Algoritmo de firma
    'ALGORITHM': 'HS256',
    
    # Header de autorización
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    
    # Claims del token
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    # Serializers custom (opcional)
    # 'TOKEN_OBTAIN_SERIALIZER': 'apps.auth.api.serializers.CustomTokenObtainPairSerializer',
}

# ==============================================================================
# REDIS CACHE 
# ==============================================================================
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',  # redis es el nombre del servicio en docker-compose
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'minimum_api',  # Prefijo para todas las keys
        'TIMEOUT': 300,  # Timeout por defecto (5 minutos)
    }
}

# Cache para sessions (opcional, si quieres usar Redis para sesiones)
# SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
# SESSION_CACHE_ALIAS = 'default'

# ==============================================================================
# LOGGING 
# ==============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file_errors': {
            'class': 'logging.FileHandler',
            'filename': 'logs/errors.log',
            'formatter': 'verbose',
            'level': 'ERROR',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    
    'loggers': {
        # Apps propias
        'apps': {
            'handlers': ['console', 'file_errors'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Django
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        # Requests externos
        'django.request': {
            'handlers': ['console', 'file_errors'],
            'level': 'ERROR',
            'propagate': False,
        },
        # Queries SQL (solo en DEBUG)
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}
# ==============================================================================
# DRF SPECTACULAR (Swagger/OpenAPI)
# ==============================================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'Minimum API',
    'DESCRIPTION': 'API REST con Django + DRF + JWT para gestión de usuarios y autenticación',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    
    # Configuración de seguridad (JWT)
    'COMPONENT_SPLIT_REQUEST': True,
    'SECURITY': [
        {
            'Bearer': []
        }
    ],
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Authorization header usando Bearer scheme. Ejemplo: "Bearer {token}"'
        }
    },
    
    # UI settings
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,
    },
    
    # Tags para agrupar endpoints
    'TAGS': [
        {'name': 'auth', 'description': 'Autenticación y autorización'},
        {'name': 'users', 'description': 'Gestión de usuarios'},
        {'name': 'groups', 'description': 'Roles y grupos'},
        {'name': 'health', 'description': 'Health check'},
    ],
}

# --------------------------------
# Internacionalización
# --------------------------------
LANGUAGE_CODE = "es-do"

TIME_ZONE = "America/Santo_Domingo"

USE_I18N = True
USE_TZ = True

# --------------------------------
# Static files
# --------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
