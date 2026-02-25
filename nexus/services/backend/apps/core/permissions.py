"""
apps/core/permissions.py

Helpers reutilizables para chequear permisos.

¿Por qué esto?
- DRY: Lógica de permisos centralizada
- Cache: Reduce queries a DB
- Claridad: Código más legible en views/services
"""
from functools import wraps
from django.core.cache import cache
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


def get_user_permissions_cached(user):
    """
    Obtiene permisos del usuario desde cache (Redis).
    
    ¿Por qué cache?
    - Los permisos no cambian frecuentemente
    - Evitamos JOIN pesado (User → Groups → Permissions)
    - Respuesta API más rápida
    
    TTL: 1 hora (se invalida al cambiar grupos/permisos)
    
    Returns:
        set: {'users.view_user', 'users.add_user', ...}
    """
    if not user or not user.is_authenticated:
        return set()
    
    cache_key = f'user_permissions:{user.id}'
    cached_perms = cache.get(cache_key)
    
    if cached_perms is not None:
        return cached_perms
    
    # Calcular permisos (incluye grupos + permisos directos)
    perms = user.get_all_permissions()
    
    # Cachear por 1 hora
    cache.set(cache_key, perms, timeout=3600)
    
    return perms


def invalidate_user_permissions_cache(user_id):
    """
    Invalida el cache de permisos de un usuario.
    
    ¿Cuándo llamar esto?
    - Al asignar/remover grupos
    - Al cambiar permisos de un grupo
    - Al asignar permisos directos al usuario
    """
    cache_key = f'user_permissions:{user_id}'
    cache.delete(cache_key)


def has_permission(user, permission_codename):
    """
    Verifica si un usuario tiene un permiso específico.
    
    Args:
        user: Usuario a verificar
        permission_codename: 'app.codename' (ej: 'users.view_user')
    
    Returns:
        bool
    
    Ejemplo:
        if has_permission(request.user, 'users.delete_user'):
            # Permitir borrado
    """
    perms = get_user_permissions_cached(user)
    return permission_codename in perms


def require_permission(permission_codename):
    """
    Decorador para servicios que requieren permiso específico.
    
    Uso en services.py:
        @require_permission('users.add_user')
        def create_user(self, data):
            # Solo se ejecuta si tiene permiso
    
    Lanza PermissionDenied si no tiene permiso.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Asumimos que self tiene self.user
            if not hasattr(self, 'user'):
                raise AttributeError(
                    f"Service {self.__class__.__name__} debe tener atributo 'user'"
                )
            
            if not has_permission(self.user, permission_codename):
                raise PermissionDenied(
                    f"No tienes permiso: {permission_codename}"
                )
            
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


class HasPermission(BasePermission):
    """
    Permission class de DRF reutilizable.
    
    Uso en views:
        class UserViewSet(viewsets.ModelViewSet):
            permission_classes = [HasPermission]
            required_permissions = {
                'list': ['users.view_user'],
                'retrieve': ['users.view_user'],
                'create': ['users.add_user'],
                'update': ['users.change_user'],
                'destroy': ['users.delete_user'],
            }
    
    ¿Por qué esto vs IsAuthenticated?
    - IsAuthenticated: Solo verifica login
    - HasPermission: Verifica permisos específicos por acción
    """
    
    def has_permission(self, request, view):
        """Verifica permisos antes de ejecutar la vista"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superuser siempre pasa
        if request.user.is_superuser:
            return True
        
        # Obtener permisos requeridos para esta acción
        required_perms = getattr(view, 'required_permissions', {})
        action = getattr(view, 'action', None)
        
        if not action or action not in required_perms:
            # Si no se especifica, requiere autenticación solamente
            return True
        
        # Verificar cada permiso requerido
        user_perms = get_user_permissions_cached(request.user)
        action_perms = required_perms[action]
        
        # Si es string, convertir a lista
        if isinstance(action_perms, str):
            action_perms = [action_perms]
        
        # Verificar que tenga TODOS los permisos requeridos
        return all(perm in user_perms for perm in action_perms)
