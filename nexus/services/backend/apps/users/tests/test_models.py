"""
apps/users/tests/test_models.py

Tests de ejemplo para UserProfile model
"""
from django.test import TestCase
from django.contrib.auth.models import User, Group
from apps.users.domain.models import UserProfile


class UserProfileModelTest(TestCase):
    """Tests para el modelo UserProfile"""
    
    def setUp(self):
        """Setup ejecutado antes de cada test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_profile_created_automatically(self):
        """Verificar que el profile se crea automáticamente vía signal"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
    
    def test_full_name_property(self):
        """Verificar propiedad full_name"""
        expected = 'Test User'
        self.assertEqual(self.user.profile.full_name, expected)
    
    def test_full_name_fallback_to_username(self):
        """Si no hay first_name/last_name, usar username"""
        user2 = User.objects.create_user(username='noname', password='pass')
        self.assertEqual(user2.profile.full_name, 'noname')
    
    def test_roles_property(self):
        """Verificar propiedad roles retorna nombres de grupos"""
        group1 = Group.objects.create(name='Administradores')
        group2 = Group.objects.create(name='Operadores')
        
        self.user.groups.add(group1, group2)
        
        roles = self.user.profile.roles
        self.assertEqual(len(roles), 2)
        self.assertIn('Administradores', roles)
        self.assertIn('Operadores', roles)
    
    def test_profile_fields(self):
        """Verificar campos adicionales del profile"""
        profile = self.user.profile
        profile.phone = '+1234567890'
        profile.department = 'IT'
        profile.employee_id = 'EMP001'
        profile.save()
        
        profile.refresh_from_db()
        
        self.assertEqual(profile.phone, '+1234567890')
        self.assertEqual(profile.department, 'IT')
        self.assertEqual(profile.employee_id, 'EMP001')
    
    def test_soft_delete(self):
        """Verificar que soft delete funciona"""
        profile = self.user.profile
        
        # Soft delete
        profile.delete()
        
        # Profile sigue en DB pero con deleted_at
        profile.refresh_from_db()
        self.assertIsNotNone(profile.deleted_at)
        self.assertTrue(profile.is_deleted)
    
    def test_restore_after_soft_delete(self):
        """Verificar que restore funciona"""
        profile = self.user.profile
        profile.delete()
        
        # Restaurar
        profile.restore()
        
        profile.refresh_from_db()
        self.assertIsNone(profile.deleted_at)
        self.assertFalse(profile.is_deleted)


# Ejecutar tests:
# python manage.py test apps.users.tests.test_models