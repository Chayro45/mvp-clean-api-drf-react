"""
apps/users/application/services.py

Service layer: Lógica de negocio de usuarios.

¿Por qué separar lógica en services?
- Views delgadas: Solo validan y delegan
- Testeable: Lógica sin HTTP
- Reutilizable: Mismo código para API, CLI, Celery tasks, etc.
- Single Responsibility: Service solo hace lógica de negocio

Patrón:
View → Service → Model
    ↓
Validación   Lógica     Persistencia
"""
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.core.permissions import require_permission, invalidate_user_permissions_cache


class UserService:
    """
    Service para gestión de usuarios.
    
    Centraliza toda la lógica de negocio:
    - Validaciones complejas
    - Transacciones
    - Invalidación de cache
    - Logging/auditoría
    
    Uso:
        service = UserService(user=request.user)
        new_user = service.create_user(validated_data)
    """
    
    def __init__(self, user):
        """
        Args:
            user: Usuario que ejecuta la acción (para permisos/auditoría)
        """
        self.user = user

    @require_permission('auth.add_user')
    def create_user(self, validated_data):
        """
        Crea un nuevo usuario.
        
        Lógica de negocio:
        1. Validar username único
        2. Crear User (password hasheado automáticamente en serializer)
        3. Profile se crea automáticamente por signal
        4. Asignar grupos
        5. Log de auditoría
        
        Args:
            validated_data: Datos validados del serializer
        
        Returns:
            User: Usuario creado
        
        Raises:
            ValidationError: Si username ya existe
        """
        # Esta lógica ya está en UserCreateSerializer.create()
        # Aquí podríamos agregar validaciones adicionales de negocio
        
        # Ejemplo: Validar que no se creen más de X usuarios activos
        max_users = 10  # Límite de plan
        active_users = User.objects.filter(is_active=True).count()
        if active_users >= max_users:
            raise ValidationError(
                f"Límite de usuarios alcanzado ({max_users}). "
                "Contacta soporte para ampliar tu plan."
            )
        
        # El serializer ya maneja la creación completa
        # Este método es un wrapper para agregar lógica extra si se necesita
        
        # TODO: Agregar logging/auditoría
        # AuditLog.objects.create(
        #     user=self.user,
        #     action='user_created',
        #     target=new_user,
        #     metadata={'groups': group_ids}
        # )
        
        return validated_data  # Se retorna para que el serializer lo procese

    @require_permission('auth.change_user')
    def update_user(self, user_instance, validated_data):
        """
        Actualiza un usuario existente.
        
        Lógica de negocio:
        1. Validar que no se desactive a sí mismo
        2. Actualizar User y Profile
        3. Invalidar cache de permisos si cambió grupos
        4. Log de auditoría
        
        Args:
            user_instance: Usuario a actualizar
            validated_data: Datos validados
        
        Returns:
            User: Usuario actualizado
        
        Raises:
            PermissionDenied: Si intenta desactivarse a sí mismo
        """
        # Validación: No puede desactivarse a sí mismo
        if (user_instance.id == self.user.id and 
            'is_active' in validated_data and 
            not validated_data['is_active']):
            raise PermissionDenied(
                "No puedes desactivar tu propia cuenta"
            )
        
        # Validación: No puede removerse sus propios permisos de admin
        if (user_instance.id == self.user.id and 
            'group_ids' in validated_data):
            # Verificar que no se quite el grupo de admin
            current_groups = set(user_instance.groups.values_list('id', flat=True))
            new_groups = set(validated_data.get('group_ids', []))
            
            # Si se está removiendo grupos y es admin...
            from django.contrib.auth.models import Group
            admin_group = Group.objects.filter(name='Administradores').first()
            if admin_group and admin_group.id in current_groups:
                if admin_group.id not in new_groups:
                    raise PermissionDenied(
                        "No puedes remover tu propio rol de Administrador"
                    )
        
        # El serializer maneja la actualización
        # Aquí podríamos agregar lógica adicional
        
        # TODO: Auditoría
        # AuditLog.objects.create(...)
        
        return validated_data

    @require_permission('auth.delete_user')
    @transaction.atomic
    def delete_user(self, user_instance):
        """
        Soft delete de usuario.
        
        NO borra de DB, solo:
        1. Marca is_active = False
        2. Soft delete del profile
        3. Invalida cache
        4. Log de auditoría
        
        Args:
            user_instance: Usuario a eliminar
        
        Raises:
            PermissionDenied: Si intenta borrarse a sí mismo
        """
        # Validación: No puede borrarse a sí mismo
        if user_instance.id == self.user.id:
            raise PermissionDenied(
                "No puedes eliminar tu propia cuenta"
            )
        
        # Soft delete
        user_instance.is_active = False
        user_instance.save()
        
        # Soft delete del profile
        if hasattr(user_instance, 'profile'):
            user_instance.profile.delete()  # Usa soft delete de BaseModel
        
        # Invalidar cache
        invalidate_user_permissions_cache(user_instance.id)
        
        # TODO: Auditoría
        # AuditLog.objects.create(
        #     user=self.user,
        #     action='user_deleted',
        #     target=user_instance
        # )

    def get_user_stats(self, user_instance):
        """
        Obtiene estadísticas del usuario.
        
        Ejemplo de método adicional que podría agregarse.
        
        Returns:
            dict: {
                'total_logins': 123,
                'last_login': datetime,
                'created_at': datetime,
                'days_since_creation': 45,
            }
        """
        from django.utils import timezone
        
        stats = {
            'last_login': user_instance.last_login,
            'created_at': user_instance.date_joined,
            'is_active': user_instance.is_active,
        }
        
        if user_instance.date_joined:
            days_since = (timezone.now() - user_instance.date_joined).days
            stats['days_since_creation'] = days_since
        
        return stats


class UserPermissionService:
    """
    Service específico para gestión de permisos.
    
    Separado de UserService para seguir Single Responsibility.
    """
    
    def __init__(self, user):
        self.user = user

    def get_user_effective_permissions(self, user_instance):
        """
        Obtiene todos los permisos efectivos del usuario.
        
        Incluye:
        - Permisos directos
        - Permisos de grupos
        - Cached en Redis
        
        Returns:
            dict: {
                'permissions': ['users.view_user', ...],
                'roles': ['Administrador', ...],
                'is_superuser': bool
            }
        """
        from apps.core.permissions import get_user_permissions_cached
        
        return {
            'permissions': list(get_user_permissions_cached(user_instance)),
            'roles': list(user_instance.groups.values_list('name', flat=True)),
            'is_superuser': user_instance.is_superuser,
        }

    @require_permission('auth.change_user')
    def assign_role(self, user_instance, group_id):
        """
        Asigna un rol (grupo) a un usuario.
        
        Args:
            user_instance: Usuario
            group_id: ID del grupo a asignar
        """
        from django.contrib.auth.models import Group
        
        group = Group.objects.get(id=group_id)
        user_instance.groups.add(group)
        
        # Invalidar cache
        invalidate_user_permissions_cache(user_instance.id)

    @require_permission('auth.change_user')
    def remove_role(self, user_instance, group_id):
        """
        Remueve un rol (grupo) de un usuario.
        
        Args:
            user_instance: Usuario
            group_id: ID del grupo a remover
        """
        from django.contrib.auth.models import Group
        
        group = Group.objects.get(id=group_id)
        user_instance.groups.remove(group)
        
        # Invalidar cache
        invalidate_user_permissions_cache(user_instance.id)
