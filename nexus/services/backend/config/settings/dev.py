from .base import *

# --------------------------------
# Entorno desarrollo
# --------------------------------
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    'backend',  # Nombre del servicio en docker-compose
    '*',  # Solo para desarrollo, NUNCA en producción
]

# DJANGO EXTENSIONS
INSTALLED_APPS += ['django_extensions']

# ==============================================================================
# CORS - ABIERTO PARA DESARROLLO (RESTRICTIVO EN PRODUCCIÓN)
# ==============================================================================
# Permitir todos los orígenes en desarrollo
# CORS_ALLOW_ALL_ORIGINS = True

# Alternativamente, especificar orígenes permitidos:
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # React dev server
    'http://localhost:5173',  # Vite dev server
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5173',
]

# Permitir cookies en CORS
CORS_ALLOW_CREDENTIALS = True

# Headers permitidos
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Métodos HTTP permitidos
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# ==============================================================================
# SECURITY - RELAJADO EN DEV (ESTRICTO EN PROD)
# ==============================================================================
# CSRF (puede deshabilitarse para API pura, pero mejor dejarlo)
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5173',
]
# Session cookie
SESSION_COOKIE_SECURE = False  # True en producción (requiere HTTPS)
CSRF_COOKIE_SECURE = False  # True en producción

# ==============================================================================
# JWT - CONFIGURACIÓN EXTENDIDA PARA DEV (TOKENS MÁS LARGOS)
# ==============================================================================
# En dev podemos extender la vida de los tokens para facilitar testing
# SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(hours=24)  # Descomentar si quieres tokens largos en dev

# ==============================================================================
# EMAIL - BACKEND DE CONSOLA PARA DEV
# ==============================================================================
# Los emails se imprimen en consola en lugar de enviarse
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ==============================================================================
# LOGGING - MÁS VERBOSE EN DEV
# ==============================================================================
LOGGING['loggers']['apps']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'INFO'

# Log de queries SQL (útil para debug, pero puede ser muy verbose)
# LOGGING['loggers']['django.db.backends'] = {
#     'handlers': ['console'],
#     'level': 'DEBUG',
#     'propagate': False,
# }

# ==============================================================================
# DEBUG TOOLBAR (OPCIONAL - MUY ÚTIL PARA DESARROLLO)
# ==============================================================================
# Descomentar si instalas django-debug-toolbar
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
# INTERNAL_IPS = ['127.0.0.1', 'localhost']

# ==============================================================================
# CACHE - DESARROLLO CON REDIS (O DUMMY CACHE SI NO QUIERES REDIS)
# ==============================================================================
# Si no quieres usar Redis en dev, puedes usar DummyCache:
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#     }
# }