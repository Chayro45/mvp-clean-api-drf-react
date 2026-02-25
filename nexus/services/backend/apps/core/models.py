"""
apps/core/models.py

Modelos base abstractos para reutilizar en todas las apps.

¿Por qué esto?
- DRY: Evitamos repetir created_at/updated_at en cada modelo
- Soft Delete: Podemos "borrar" sin eliminar de DB (auditoría)
- Pragmático: Solo lo esencial, sin sobre-ingeniería
"""
from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    """
    Modelo abstracto que agrega timestamps automáticos.
    
    Uso:
        class MyModel(TimestampedModel):
            name = models.CharField(max_length=100)
    
    Resultado:
        - created_at se setea automáticamente al crear
        - updated_at se actualiza en cada save()
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        db_index=True,  # Para queries por fecha
        verbose_name="Creado el"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
        verbose_name="Actualizado el"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']  # Más recientes primero por defecto


class SoftDeleteModel(models.Model):
    """
    Modelo abstracto para soft delete (borrado lógico).
    
    ¿Por qué soft delete?
    - Auditoría: Sabemos quién borró qué y cuándo
    - Recuperación: Podemos "deshacer" borrados
    - Compliance: Algunos regulatorios requieren no borrar data
    
    Uso:
        class MyModel(SoftDeleteModel):
            name = models.CharField(max_length=100)
        
        obj.delete()  # Solo marca deleted_at, no borra de DB
        obj.hard_delete()  # Borra realmente de DB
    """
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        db_index=True,
        verbose_name="Eliminado el"
    )

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft delete: marca deleted_at en lugar de borrar"""
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def hard_delete(self, using=None, keep_parents=False):
        """Hard delete: borra realmente de la base de datos"""
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """Restaura un objeto soft-deleted"""
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])

    @property
    def is_deleted(self):
        """Verifica si el objeto está soft-deleted"""
        return self.deleted_at is not None


class BaseModel(TimestampedModel, SoftDeleteModel):
    """
    Modelo base que combina timestamps + soft delete.
    
    La mayoría de nuestros modelos heredarán de este.
    
    Uso:
        class Product(BaseModel):
            name = models.CharField(max_length=100)
            price = models.DecimalField(max_digits=10, decimal_places=2)
    
    Resultado automático:
        - created_at
        - updated_at
        - deleted_at
        - métodos: delete(), hard_delete(), restore()
    """
    class Meta:
        abstract = True
