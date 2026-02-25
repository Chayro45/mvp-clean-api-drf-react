"""
apps/core/management/commands/createsuperuser_auto.py

Management command para crear superusuario automáticamente.

Ejecutar:
    python manage.py createsuperuser_auto

¿Cuándo se ejecuta?
- Automáticamente en docker-compose (al iniciar backend)
- Manualmente en desarrollo
- Es idempotente (no duplica si ya existe)

Crea:
- Usuario: admin
- Password: admin (solo para desarrollo)
- Email: admin@example.com
- Superuser: True
- Staff: True
- Grupo: Administradores (si existe)

IMPORTANTE:
- Solo para desarrollo
- En producción, cambiar password inmediatamente
- O mejor, crear usuario admin manualmente
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea un superusuario automáticamente (solo desarrollo)'

    def add_arguments(self, parser):
        """Argumentos opcionales"""
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username del superusuario (default: admin)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin',
            help='Password del superusuario (default: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@example.com',
            help='Email del superusuario (default: admin@example.com)'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        
        self.stdout.write(self.style.SUCCESS('👤 Verificando superusuario...'))
        
        # Verificar si ya existe
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'  → Usuario "{username}" ya existe, omitiendo...')
            )
            return
        
        # Crear superusuario
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='CTC Nexus Admin',
                last_name='User',
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'  ✓ Superusuario "{username}" creado exitosamente')
            )
            
            # Asignar al grupo Administradores (si existe)
            try:
                admin_group = Group.objects.get(name='Administradores')
                user.groups.add(admin_group)
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Asignado al grupo "Administradores"')
                )
            except Group.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING('  → Grupo "Administradores" no existe (ejecuta seed_roles primero)')
                )
            
            # Mostrar credenciales (solo en desarrollo)
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('=' * 60))
            self.stdout.write(self.style.SUCCESS('✅ Superusuario creado'))
            self.stdout.write(self.style.SUCCESS('=' * 60))
            self.stdout.write(self.style.WARNING('⚠️  CREDENCIALES DE DESARROLLO:'))
            self.stdout.write(f'    Username: {username}')
            self.stdout.write(f'    Password: {password}')
            self.stdout.write(f'    Email: {email}')
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('⚠️  CAMBIAR PASSWORD EN PRODUCCIÓN ⚠️'))
            self.stdout.write('')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ✗ Error al crear superusuario: {str(e)}')
            )