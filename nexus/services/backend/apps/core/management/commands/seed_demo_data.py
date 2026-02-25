
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Crea datos de ejemplo para testing'
    
    def handle(self, *args, **options):
        # Crear usuarios de ejemplo
        operator_group = Group.objects.get(name='Operadores')
        
        users = [
            {
                'username': 'operator1',
                'email': 'op1@example.com',
                'password': 'demo123',
                'first_name': 'Juan',
                'last_name': 'Operador',
            },
            {
                'username': 'operator2',
                'email': 'op2@example.com',
                'password': 'demo123',
                'first_name': 'María',
                'last_name': 'González',
            },
        ]
        
        for user_data in users:
            password = user_data.pop('password')
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            
            if created:
                user.set_password(password)
                user.save()
                user.groups.add(operator_group)
                
                # Actualizar profile
                user.profile.department = 'Operaciones'
                user.profile.phone = '+1234567890'
                user.profile.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Usuario {user.username} creado')
                )