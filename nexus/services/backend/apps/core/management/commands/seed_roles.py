"""
apps/core/management/commands/seed_roles.py

Management command para crear grupos (roles) y asignar permisos.

Ejecutar:
    python manage.py seed_roles

¿Cuándo se ejecuta?
- Automáticamente en docker-compose (al iniciar backend)
- Manualmente después de migrate
- En cada deploy (es idempotente, no duplica)

Crea:
- Grupo "Administradores" con todos los permisos
- Grupo "Operadores" con permisos de lectura
- Grupo "Usuarios" con permisos básicos
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea grupos (roles) y asigna permisos iniciales'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📦 Iniciando seed de roles y permisos...'))
        
        # Definir roles y sus permisos
        roles_config = {
            'Administradores': {
                'description': 'Acceso total al sistema',
                'permissions': 'all',  # Todos los permisos
            },
            'Operadores': {
                'description': 'Puede ver y editar usuarios',
                'permissions': [
                    'auth.view_user',
                    'auth.add_user',
                    'auth.change_user',
                    # NO tiene delete_user
                ],
            },
            'Usuarios': {
                'description': 'Solo puede ver usuarios',
                'permissions': [
                    'auth.view_user',
                ],
            },
        }
        
        for role_name, config in roles_config.items():
            # Crear o obtener grupo
            group, created = Group.objects.get_or_create(name=role_name)
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Grupo "{role_name}" creado')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  → Grupo "{role_name}" ya existe, actualizando permisos...')
                )
            
            # Limpiar permisos existentes
            group.permissions.clear()
            
            # Asignar permisos
            if config['permissions'] == 'all':
                # Administradores: todos los permisos
                all_permissions = Permission.objects.all()
                group.permissions.set(all_permissions)
                self.stdout.write(
                    self.style.SUCCESS(f'    → {all_permissions.count()} permisos asignados (TODOS)')
                )
            else:
                # Otros roles: permisos específicos
                permissions_added = 0
                for perm_code in config['permissions']:
                    try:
                        app_label, codename = perm_code.split('.')
                        permission = Permission.objects.get(
                            content_type__app_label=app_label,
                            codename=codename
                        )
                        group.permissions.add(permission)
                        permissions_added += 1
                    except Permission.DoesNotExist:
                        self.stdout.write(
                            self.style.ERROR(f'    ✗ Permiso no encontrado: {perm_code}')
                        )
                    except ValueError:
                        self.stdout.write(
                            self.style.ERROR(f'    ✗ Formato inválido: {perm_code}')
                        )
                
                self.stdout.write(
                    self.style.SUCCESS(f'    → {permissions_added} permisos asignados')
                )
        
        # Resumen
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('✅ Seed de roles completado'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')
        
        # Mostrar resumen de grupos
        for group in Group.objects.all():
            perm_count = group.permissions.count()
            self.stdout.write(
                f'  📋 {group.name}: {perm_count} permisos'
            )
        
        self.stdout.write('')

    def _show_available_permissions(self):
        """Helper para mostrar permisos disponibles (debugging)"""
        self.stdout.write(self.style.WARNING('\nPermisos disponibles:'))
        for perm in Permission.objects.select_related('content_type').all():
            self.stdout.write(
                f'  - {perm.content_type.app_label}.{perm.codename} | {perm.name}'
            )