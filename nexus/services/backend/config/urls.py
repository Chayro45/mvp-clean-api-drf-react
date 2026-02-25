from django.contrib import admin # pyright: ignore[reportMissingModuleSource]
from django.urls import path, include # pyright: ignore[reportMissingModuleSource]
from django.conf import settings # pyright: ignore[reportMissingModuleSource]
from django.conf.urls.static import static # pyright: ignore[reportMissingModuleSource]
from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularSwaggerView,
        SpectacularRedocView,
    )

urlpatterns = [
     # Swagger / OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Admin de Django
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/auth/', include('apps.auth.api.urls')),  # Autenticación
    path('api/users/', include('apps.users.api.urls')),  # Usuarios
    
    # Health check (útil para Docker, K8s, load balancers)
    path('health/', include('apps.core.urls')),  # Vamos a crear esto después
]

# Servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Debug Toolbar (solo en desarrollo)
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

# Personalizar admin
admin.site.site_header = "Minimum API Admin"
admin.site.site_title = "Minimum API"
admin.site.index_title = "Panel de Administración"

"""
RUTAS DISPONIBLES:
==================

AUTENTICACIÓN:
--------------
POST   /api/auth/login/       → Login (obtener tokens)
POST   /api/auth/refresh/     → Refresh access token
POST   /api/auth/logout/      → Logout (blacklist token)
POST   /api/auth/verify/      → Verificar token
GET    /api/auth/me/          → Usuario actual

USUARIOS:
---------
GET    /api/users/            → Listar usuarios
POST   /api/users/            → Crear usuario
GET    /api/users/{id}/       → Ver usuario
PUT    /api/users/{id}/       → Actualizar usuario
PATCH  /api/users/{id}/       → Actualizar parcial
DELETE /api/users/{id}/       → Eliminar usuario (soft delete)
GET    /api/users/me/         → Mi usuario (shortcut)
POST   /api/users/{id}/change_password/  → Cambiar password
GET    /api/users/groups/     → Listar grupos (roles)

ADMIN:
------
GET    /admin/                → Django admin

HEALTH CHECK:
-------------
GET    /health/               → Health check (lo crearemos)
"""
