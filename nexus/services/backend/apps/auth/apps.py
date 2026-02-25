"""
apps/auth/apps.py

Configuración de la app auth.

NOTA: Esta app se llama 'apps.auth' para no confundirse con 'django.contrib.auth'
"""
from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.auth'
    verbose_name = 'Autenticación'
    # Label único para evitar conflicto con django.contrib.auth
    label = 'apps_auth'
