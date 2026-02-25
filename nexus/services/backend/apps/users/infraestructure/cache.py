"""
apps/users/infrastructure/cache.py

Capa de infraestructura: Cache de permisos en Redis.

¿Por qué separar cache en infrastructure?
- Desacoplamiento: Si cambiamos Redis por Memcached, solo tocamos aquí
- Testeable: Fácil mockear en tests
- Reutilizable: Otros services pueden usar estas funciones

Decisión técnica: Redis
- Rápido: <1ms para get
- Persistente: Sobrevive reinicio (opcional)
- Estructuras de datos: Sets, Hashes, Lists
- Pub/Sub: Para invalidación distribuida (futuro)
"""
from django.core.cache import cache
from django.contrib.auth.models import User
from typing import Set, Optional
import logging

logger = logging.getLogger(__name__)


class UserPermissionCache:
    """
    Gestión de cache de permisos de usuario en Redis.
    
    Estrategia de cache:
    - Key: user_permissions:{user_id}
    - Value: Set de permisos (JSON serializable)
    - TTL: 1 hora (3600s)
    - Invalidación: Manual al cambiar grupos/permisos
    
    ¿Por qué cachear permisos?
    - Cada request autenticado chequea permisos
    - Sin cache: JOIN pesado User → Groups → Permissions
    - Con cache: Simple GET de Redis
    - Impacto: 50-200ms → <1ms por request
    """
    
    CACHE_KEY_PREFIX = 'user_permissions'
    CACHE_TTL = 3600  # 1 hora
    
    @classmethod
    def _make_key(cls, user_id: int) -> str:
        """
        Genera cache key para un usuario.
        
        Args:
            user_id: ID del usuario
        
        Returns:
            str: 'user_permissions:123'
        """
        return f"{cls.CACHE_KEY_PREFIX}:{user_id}"
    
    @classmethod
    def get(cls, user_id: int) -> Optional[Set[str]]:
        """
        Obtiene permisos del cache.
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Set[str] | None: Set de permisos o None si no está en cache
            
        Example:
            perms = UserPermissionCache.get(123)
            # {'users.view_user', 'users.add_user'}
        """
        key = cls._make_key(user_id)
        cached = cache.get(key)
        
        if cached is not None:
            logger.debug(f"Cache HIT para permisos de usuario {user_id}")
            return set(cached)  # Convertir de list a set
        
        logger.debug(f"Cache MISS para permisos de usuario {user_id}")
        return None
    
    @classmethod
    def set(cls, user_id: int, permissions: Set[str]) -> None:
        """
        Guarda permisos en cache.
        
        Args:
            user_id: ID del usuario
            permissions: Set de permisos
            
        Example:
            UserPermissionCache.set(123, {'users.view_user', 'users.add_user'})
        """
        key = cls._make_key(user_id)
        # Convertir set a list para serialización JSON
        cache.set(key, list(permissions), timeout=cls.CACHE_TTL)
        logger.debug(f"Cache SET para permisos de usuario {user_id} (TTL: {cls.CACHE_TTL}s)")
    
    @classmethod
    def delete(cls, user_id: int) -> None:
        """
        Invalida cache de permisos de un usuario.
        
        Llamar cuando:
        - Se asigna/remueve un grupo al usuario
        - Se cambian permisos de un grupo del usuario
        - Se asignan permisos directos al usuario
        
        Args:
            user_id: ID del usuario
            
        Example:
            user.groups.add(admin_group)
            UserPermissionCache.delete(user.id)  # Invalidar cache
        """
        key = cls._make_key(user_id)
        cache.delete(key)
        logger.info(f"Cache INVALIDADO para permisos de usuario {user_id}")
    
    @classmethod
    def get_or_compute(cls, user_id: int) -> Set[str]:
        """
        Obtiene permisos del cache o los calcula si no existen.
        
        Pattern: Cache-aside (lazy loading)
        1. Intenta obtener de cache
        2. Si no existe, calcula de DB
        3. Guarda en cache
        4. Retorna
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Set[str]: Set de permisos
            
        Example:
            perms = UserPermissionCache.get_or_compute(123)
        """
        # Intentar obtener de cache
        cached = cls.get(user_id)
        if cached is not None:
            return cached
        
        # No está en cache, calcular de DB
        try:
            user = User.objects.get(id=user_id)
            permissions = user.get_all_permissions()
            
            # Guardar en cache
            cls.set(user_id, permissions)
            
            return permissions
            
        except User.DoesNotExist:
            logger.warning(f"Usuario {user_id} no existe")
            return set()
    
    @classmethod
    def invalidate_group(cls, group_id: int) -> None:
        """
        Invalida cache de todos los usuarios de un grupo.
        
        Llamar cuando:
        - Se cambian los permisos de un grupo
        - Se renombra un grupo (edge case)
        
        NOTA: Esto puede ser costoso si el grupo tiene muchos usuarios.
        En ese caso, considerar:
        - Invalidación lazy (TTL corto)
        - Pub/Sub para invalidación distribuida
        
        Args:
            group_id: ID del grupo
            
        Example:
            admin_group.permissions.add(new_permission)
            UserPermissionCache.invalidate_group(admin_group.id)
        """
        from django.contrib.auth.models import Group
        
        try:
            group = Group.objects.get(id=group_id)
            user_ids = group.user_set.values_list('id', flat=True)
            
            for user_id in user_ids:
                cls.delete(user_id)
            
            logger.info(
                f"Cache INVALIDADO para {len(user_ids)} usuarios del grupo {group.name}"
            )
            
        except Group.DoesNotExist:
            logger.warning(f"Grupo {group_id} no existe")
    
    @classmethod
    def warm_up(cls, user_ids: list = None) -> None:
        """
        Pre-carga cache de permisos (warm-up).
        
        Útil para:
        - Después de deploy
        - Cronjob nocturno
        - Antes de pico de tráfico
        
        Args:
            user_ids: Lista de IDs a pre-cargar. Si None, todos los activos.
            
        Example:
            # Pre-cargar usuarios activos
            UserPermissionCache.warm_up()
            
            # Pre-cargar usuarios específicos
            UserPermissionCache.warm_up([1, 2, 3])
        """
        if user_ids is None:
            users = User.objects.filter(is_active=True)
        else:
            users = User.objects.filter(id__in=user_ids)
        
        count = 0
        for user in users:
            cls.get_or_compute(user.id)
            count += 1
        
        logger.info(f"Cache WARM-UP completado para {count} usuarios")


# Funciones helper (retrocompatibilidad con apps.core.permissions)

def get_user_permissions_cached(user) -> Set[str]:
    """
    Helper function compatible con core.permissions.
    
    Esta función es llamada desde:
    - apps/core/permissions.py
    - Serializers
    - Services
    
    Args:
        user: Usuario de Django
    
    Returns:
        Set[str]: Set de permisos
    """
    if not user or not user.is_authenticated:
        return set()
    
    return UserPermissionCache.get_or_compute(user.id)


def invalidate_user_permissions_cache(user_id: int) -> None:
    """
    Helper function compatible con core.permissions.
    
    Args:
        user_id: ID del usuario
    """
    UserPermissionCache.delete(user_id)
