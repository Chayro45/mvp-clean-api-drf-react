# 🧪 Testing Guide

Guía completa para ejecutar y escribir tests en el proyecto.

---

## Tabla de Contenidos

- [Overview](#overview)
- [Tests Backend](#tests-backend)
- [Tests Frontend](#tests-frontend)
- [Coverage](#coverage)
- [Mejores Prácticas](#mejores-prácticas)

---

## Overview

El proyecto usa diferentes herramientas de testing según la capa:

| Capa | Herramienta | Comando |
|------|-------------|---------|
| Backend | Django unittest | `make test` |
| Backend (avanzado) | pytest + pytest-django | `pytest` |
| Frontend | Vitest | `make test-frontend` |
| E2E | Playwright | `npx playwright test` |

---

## Tests Backend

### Ejecutar Tests

```bash
# Todos los tests
make test

# O manualmente
docker exec minimum_api_backend python manage.py test

# Tests de una app específica
docker exec minimum_api_backend python manage.py test apps.users

# Test de un archivo específico
docker exec minimum_api_backend python manage.py test apps.users.tests.test_models

# Test específico
docker exec minimum_api_backend python manage.py test apps.users.tests.test_models.UserProfileModelTest.test_profile_created_automatically
```

### Con pytest (recomendado para proyectos grandes)

```bash
# Instalar pytest
pip install pytest pytest-django pytest-cov

# Ejecutar tests
docker exec minimum_api_backend pytest

# Con coverage
docker exec minimum_api_backend pytest --cov=apps --cov-report=html

# Ver reporte
open htmlcov/index.html
```

---

### Estructura de Tests

```
services/backend/apps/
├── users/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_models.py       # Tests de modelos
│   │   ├── test_serializers.py  # Tests de serializers
│   │   ├── test_views.py        # Tests de endpoints
│   │   └── test_services.py     # Tests de services
```

---

### Escribir Tests

#### 1. Test de Modelo

```python
# apps/users/tests/test_models.py

from django.test import TestCase
from django.contrib.auth.models import User
from apps.users.domain.models import UserProfile


class UserProfileModelTest(TestCase):
    """Tests para el modelo UserProfile"""
    
    def setUp(self):
        """Setup ejecutado antes de cada test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_profile_created_automatically(self):
        """Verificar que el profile se crea automáticamente"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
    
    def test_full_name_property(self):
        """Verificar propiedad full_name"""
        self.user.first_name = 'John'
        self.user.last_name = 'Doe'
        self.user.save()
        
        self.assertEqual(self.user.profile.full_name, 'John Doe')
    
    def tearDown(self):
        """Limpieza después de cada test"""
        User.objects.all().delete()
```

---

#### 2. Test de API Endpoint

```python
# apps/users/tests/test_views.py

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status


class UserAPITest(TestCase):
    """Tests para endpoints de usuarios"""
    
    def setUp(self):
        """Setup"""
        self.client = APIClient()
        
        # Crear usuario admin
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        # Obtener token JWT
        response = self.client.post('/api/auth/login/', {
            'username': 'admin',
            'password': 'admin123'
        })
        self.token = response.data['access']
        
        # Configurar auth header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_list_users(self):
        """Test GET /api/users/"""
        response = self.client.get('/api/users/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreater(response.data['count'], 0)
    
    def test_create_user(self):
        """Test POST /api/users/"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'secure123',
            'password_confirm': 'secure123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post('/api/users/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser')
        
        # Verificar que se creó en DB
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_create_user_without_auth(self):
        """Test crear usuario sin autenticación"""
        self.client.credentials()  # Remover auth
        
        response = self.client.post('/api/users/', {
            'username': 'test',
            'email': 'test@test.com',
            'password': 'pass123',
            'password_confirm': 'pass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

---

#### 3. Test de Service

```python
# apps/users/tests/test_services.py

from django.test import TestCase
from django.contrib.auth.models import User, Group
from rest_framework.exceptions import ValidationError
from apps.users.application.services import UserService


class UserServiceTest(TestCase):
    """Tests para UserService"""
    
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin',
            password='admin123'
        )
        self.service = UserService(user=self.admin)
    
    def test_create_user_validates_limit(self):
        """Test que valida límite de usuarios"""
        # Mockear límite bajo
        with patch('apps.users.application.services.MAX_USERS', 2):
            # Crear 2 usuarios (límite)
            User.objects.create_user('user1', password='pass')
            User.objects.create_user('user2', password='pass')
            
            # Intentar crear 3ro debe fallar
            with self.assertRaises(ValidationError):
                self.service.create_user({
                    'username': 'user3',
                    'email': 'user3@test.com',
                    'password': 'pass'
                })
```

---

#### 4. Test con Fixtures

```python
# apps/users/tests/test_with_fixtures.py

from django.test import TestCase
from django.contrib.auth.models import User

class UserTestWithFixtures(TestCase):
    """Tests usando fixtures"""
    
    fixtures = ['users.json', 'groups.json']
    
    def test_fixtures_loaded(self):
        """Verificar que los fixtures se cargaron"""
        self.assertGreater(User.objects.count(), 0)
```

**Crear fixture:**
```bash
# Exportar datos actuales
docker exec minimum_api_backend python manage.py dumpdata auth.User --indent 2 > fixtures/users.json
```

---

### Mocking

```python
from unittest.mock import patch, Mock

class EmailServiceTest(TestCase):
    
    @patch('django.core.mail.send_mail')
    def test_welcome_email_sent(self, mock_send_mail):
        """Test que se envía email de bienvenida"""
        service = UserService(user=self.admin)
        service._send_welcome_email(self.user)
        
        # Verificar que se llamó
        mock_send_mail.assert_called_once()
        
        # Verificar argumentos
        args, kwargs = mock_send_mail.call_args
        self.assertIn('Bienvenido', args[0])  # Subject
```

---

### Test de Cache

```python
from django.core.cache import cache

class CacheTest(TestCase):
    
    def setUp(self):
        cache.clear()
    
    def test_permissions_cached(self):
        """Test que permisos se cachean"""
        # Primera llamada: no está en cache
        with self.assertNumQueries(5):
            perms = get_user_permissions(self.user.id)
        
        # Segunda llamada: desde cache (0 queries)
        with self.assertNumQueries(0):
            cached_perms = get_user_permissions(self.user.id)
        
        self.assertEqual(perms, cached_perms)
```

---

## Tests Frontend

### Ejecutar Tests

```bash
# Todos los tests
make test-frontend

# O manualmente
docker exec minimum_api_frontend npm test

# Con coverage
docker exec minimum_api_frontend npm run test:coverage

# Watch mode (re-ejecutar al cambiar)
docker exec minimum_api_frontend npm test -- --watch
```

---

### Escribir Tests

#### Setup (vitest.config.js)

```javascript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: './src/tests/setup.js',
  },
})
```

#### 1. Test de Componente

```javascript
// src/components/common/__tests__/LoadingSpinner.test.jsx

import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import LoadingSpinner from '../LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders spinner', () => {
    render(<LoadingSpinner />)
    expect(screen.getByRole('status')).toBeInTheDocument()
  })
  
  it('displays text when provided', () => {
    render(<LoadingSpinner text="Cargando..." />)
    expect(screen.getByText('Cargando...')).toBeInTheDocument()
  })
  
  it('applies correct size class', () => {
    const { container } = render(<LoadingSpinner size="lg" />)
    const spinner = container.querySelector('.spinner')
    expect(spinner).toHaveClass('w-16', 'h-16')
  })
})
```

---

#### 2. Test de Hook

```javascript
// src/hooks/__tests__/useIdleTimeout.test.js

import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import useIdleTimeout from '../useIdleTimeout'

describe('useIdleTimeout', () => {
  it('calls onIdle after timeout', async () => {
    const onIdle = vi.fn()
    const idleTime = 1000
    
    renderHook(() => useIdleTimeout({ onIdle, idleTime }))
    
    // Esperar más del timeout
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 1100))
    })
    
    expect(onIdle).toHaveBeenCalledOnce()
  })
  
  it('resets timer on activity', async () => {
    const onIdle = vi.fn()
    const { result } = renderHook(() => 
      useIdleTimeout({ onIdle, idleTime: 1000 })
    )
    
    // Simular actividad
    act(() => {
      result.current.resetTimer()
    })
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 1100))
    })
    
    expect(onIdle).toHaveBeenCalledOnce()
  })
})
```

---

#### 3. Test de Service

```javascript
// src/services/__tests__/authService.test.js

import { describe, it, expect, vi, beforeEach } from 'vitest'
import authService from '../authService'
import api from '../api'

vi.mock('../api')

describe('authService', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })
  
  it('login stores tokens', async () => {
    const mockResponse = {
      data: {
        access: 'access-token',
        refresh: 'refresh-token',
        user: { id: 1, username: 'test' }
      }
    }
    
    api.post.mockResolvedValue(mockResponse)
    
    await authService.login('test', 'pass123')
    
    expect(localStorage.getItem('access_token')).toBe('access-token')
    expect(localStorage.getItem('refresh_token')).toBe('refresh-token')
  })
  
  it('logout clears storage', async () => {
    localStorage.setItem('access_token', 'token')
    localStorage.setItem('refresh_token', 'token')
    
    await authService.logout()
    
    expect(localStorage.getItem('access_token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
  })
})
```

---

## Coverage

### Backend

```bash
# Con pytest
docker exec minimum_api_backend pytest --cov=apps --cov-report=html --cov-report=term

# Ver reporte HTML
open htmlcov/index.html

# O con coverage.py
docker exec minimum_api_backend coverage run --source='apps' manage.py test
docker exec minimum_api_backend coverage report
docker exec minimum_api_backend coverage html
```

**Meta de coverage:** 80%+

---

### Frontend

```bash
# Con vitest
docker exec minimum_api_frontend npm run test:coverage

# Ver reporte
open coverage/index.html
```

---

## Tests E2E (End-to-End)

### Con Playwright

```bash
# Instalar
npm install -D @playwright/test

# Ejecutar
npx playwright test

# UI mode
npx playwright test --ui

# Debug
npx playwright test --debug
```

### Ejemplo de Test E2E

```javascript
// e2e/auth.spec.js

import { test, expect } from '@playwright/test'

test.describe('Authentication Flow', () => {
  test('user can login', async ({ page }) => {
    // Ir a login
    await page.goto('http://localhost:5173/login')
    
    // Llenar formulario
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'admin')
    
    // Submit
    await page.click('button[type="submit"]')
    
    // Verificar redirect a dashboard
    await expect(page).toHaveURL(/.*dashboard/)
    
    // Verificar contenido
    await expect(page.locator('text=Bienvenido')).toBeVisible()
  })
  
  test('invalid credentials show error', async ({ page }) => {
    await page.goto('http://localhost:5173/login')
    
    await page.fill('input[name="username"]', 'wrong')
    await page.fill('input[name="password"]', 'wrong')
    await page.click('button[type="submit"]')
    
    // Verificar error
    await expect(page.locator('text=Usuario o contraseña incorrectos')).toBeVisible()
  })
})
```

---

## Mejores Prácticas

### 1. AAA Pattern

```python
def test_user_creation():
    # Arrange (preparar)
    data = {'username': 'test', 'email': 'test@test.com'}
    
    # Act (ejecutar)
    user = User.objects.create(**data)
    
    # Assert (verificar)
    assert user.username == 'test'
```

### 2. Tests Independientes

```python
# ❌ Malo (tests dependen uno del otro)
class BadTest(TestCase):
    def test_01_create(self):
        self.user = User.objects.create(username='test')
    
    def test_02_update(self):
        self.user.email = 'new@test.com'  # Depende de test_01

# ✅ Bueno (cada test es independiente)
class GoodTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test')
    
    def test_create(self):
        assert self.user.username == 'test'
    
    def test_update(self):
        self.user.email = 'new@test.com'
        self.user.save()
        assert self.user.email == 'new@test.com'
```

### 3. Nombres Descriptivos

```python
# ❌ Malo
def test_1():
    pass

# ✅ Bueno
def test_user_profile_created_automatically_when_user_created():
    pass
```

### 4. Un Assert por Test (idealmente)

```python
# ❌ Malo (múltiples asserts dificultan debug)
def test_user():
    user = create_user()
    assert user.username == 'test'
    assert user.email == 'test@test.com'
    assert user.is_active == True

# ✅ Bueno (un concepto por test)
def test_user_has_correct_username():
    user = create_user()
    assert user.username == 'test'

def test_user_has_correct_email():
    user = create_user()
    assert user.email == 'test@test.com'
```

### 5. Usar Factories

```python
# Instalar factory_boy
pip install factory-boy

# apps/users/tests/factories.py
import factory
from django.contrib.auth.models import User

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')

# Usar en tests
def test_with_factory():
    user = UserFactory.create()  # Crea usuario con datos default
    admin = UserFactory.create(is_superuser=True)  # Override
```

---

## CI/CD Integration

```yaml
# .github/workflows/tests.yml

name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          docker-compose up -d
          docker exec minimum_api_backend python manage.py test
          
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd services/frontend
          npm install
          npm test
```

---

## Recursos

- **Django Testing**: https://docs.djangoproject.com/en/4.2/topics/testing/
- **pytest**: https://docs.pytest.org/
- **Vitest**: https://vitest.dev/
- **Playwright**: https://playwright.dev/
- **Testing Library**: https://testing-library.com/

---

**Siguiente:** [Deployment Guide](DEPLOYMENT.md)
