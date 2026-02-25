"""
apps/users/domain/models.py

Modelo de dominio: UserProfile

¿Por qué extender User con OneToOne en lugar de custom User model?
- Pragmático: Usamos el User nativo de Django (probado, robusto)
- Compatible: Funciona con todo el ecosistema Django/DRF
- Extensible: Agregamos campos custom sin tocar User
- Migraciones: No hay problemas de migración compleja

Cuando usar Custom User:
- Si necesitas cambiar el campo de login (ej: email en lugar de username)
- Si es proyecto nuevo desde cero

Cuando usar OneToOne (nuestro caso):
- Proyecto existente
- Solo necesitamos campos adicionales
- Queremos mantener compatibilidad
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.core.models import BaseModel


class UserProfile(BaseModel):
    """
    Extensión del User nativo de Django.
    
    Campos del User nativo (ya tenemos):
    - username
    - email
    - first_name
    - last_name
    - password
    - is_active
    - is_staff
    - is_superuser
    - groups (roles)
    - user_permissions
    
    Agregamos aquí:
    - Metadata adicional (teléfono, avatar, etc.)
    - Campos de negocio específicos
    - Relaciones con otras entidades
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Usuario"
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Teléfono"
    )
    
    avatar_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL del Avatar",
        help_text="URL de imagen de perfil (puede ser S3, Cloudinary, etc.)"
    )
    
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Departamento",
        help_text="Departamento o área de trabajo"
    )
    
    employee_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name="ID de Empleado",
        help_text="Identificador único de empleado en la organización"
    )
    
    # Metadata de negocio
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notas",
        help_text="Notas internas sobre el usuario"
    )

    class Meta:
        db_table = 'user_profiles'
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
        ordering = ['-created_at']

    def __str__(self):
        return f"Perfil de {self.user.username}"

    @property
    def full_name(self):
        """Nombre completo del usuario"""
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username

    @property
    def roles(self):
        """
        Retorna lista de nombres de grupos (roles) del usuario.
        
        Returns:
            list: ['Administrador', 'Operador']
        """
        return list(self.user.groups.values_list('name', flat=True))

    @property
    def permissions_list(self):
        """
        Retorna lista de permisos del usuario (desde cache).
        
        Returns:
            list: ['users.view_user', 'users.add_user', ...]
        """
        from apps.core.permissions import get_user_permissions_cached
        return list(get_user_permissions_cached(self.user))


# Signal para crear automáticamente UserProfile al crear User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crea UserProfile automáticamente cuando se crea un User.
    
    ¿Por qué signal?
    - Transparente: No hay que recordar crear el profile manualmente
    - Automático: Funciona con createsuperuser, admin, API, etc.
    - Consistencia: Todo User tiene su Profile
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Guarda el profile cuando se guarda el User.
    
    Esto asegura que si hacemos user.save(), también se guarde el profile.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
