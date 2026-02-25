"""
apps/users/apps.py

Configuración de la app users.

¿Por qué el ready() method?
- Registra signals automáticamente al cargar la app
- Asegura que UserProfile se cree cuando se crea User
"""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'Usuarios'
    
    # def ready(self):
    #     """
    #     Se ejecuta cuando Django carga la app.
        
    #     Importamos signals aquí para registrarlos.
    #     """
    #     # Importar signals para registrarlos
    #     import apps.users.domain.models  # Esto registra los @receiver decorators
