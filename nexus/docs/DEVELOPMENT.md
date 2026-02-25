# 💻 Development Guide

Guía completa para desarrolladores que quieren contribuir o extender el proyecto.

---

## Tabla de Contenidos

- [Configuración del Entorno](#configuración-del-entorno)
- [Estructura del Código](#estructura-del-código)
- [Convenciones de Código](#convenciones-de-código)
- [Agregar Nuevas Funcionalidades](#agregar-nuevas-funcionalidades)
- [Debugging](#debugging)
- [Best Practices](#best-practices)

---

## Configuración del Entorno

### Desarrollo Local (con Docker)

```bash
# Clonar y setup
git clone https://github.com/tu-usuario/minimum-api.git
cd minimum-api
cp services/backend/.env.example services/backend/.env
cp services/frontend/.env.example services/frontend/.env

# Levantar en modo desarrollo
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f
```

### Desarrollo sin Docker (avanzado)

#### Backend

```bash
cd services/backend

# Crear virtualenv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# O: venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar DATABASE_URL, REDIS_URL

# Migraciones
python manage.py migrate
python manage.py seed_roles
python manage.py createsuperuser_auto

# Correr servidor
python manage.py runserver
```

#### Frontend

```bash
cd services/frontend

# Instalar dependencias
npm install

# Configurar .env
cp .env.example .env

# Correr dev server
npm run dev
```

---

## Estructura del Código

### Backend

```
services/backend/
├── apps/
│   ├── core/                    # Funcionalidad compartida
│   │   ├── models.py           # BaseModel, TimestampedModel, SoftDeleteModel
│   │   ├── permissions.py      # Helpers de permisos y cache
│   │   ├── views.py            # HealthCheckView
│   │   └── management/
│   │       └── commands/       # Management commands
│   │
│   ├── users/                   # Gestión de usuarios
│   │   ├── domain/
│   │   │   └── models.py       # UserProfile
│   │   ├── api/
│   │   │   ├── views.py        # UserViewSet
│   │   │   ├── serializers.py  # User serializers
│   │   │   └── urls.py         # Routing
│   │   ├── application/
│   │   │   └── services.py     # UserService (lógica de negocio)
│   │   └── infrastructure/
│   │       └── cache.py        # UserPermissionCache
│   │
│   └── auth/                    # Autenticación JWT
│       ├── api/
│       │   ├── views.py        # LoginView, TokenRefreshView
│       │   ├── serializers.py  # Auth serializers
│       │   └── urls.py
│       └── application/
│           └── services.py     # AuthService
│
└── config/
    ├── settings/
    │   ├── base.py             # Config compartida
    │   ├── dev.py              # Development
    │   └── prod.py             # Production
    ├── urls.py                 # URL root
    └── wsgi.py
```

### Frontend

```
services/frontend/src/
├── components/
│   ├── auth/
│   │   ├── LoginForm.jsx       # Formulario de login
│   │   └── ProtectedRoute.jsx  # HOC para rutas protegidas
│   ├── common/
│   │   ├── Modal.jsx           # Modal reutilizable
│   │   ├── LoadingSpinner.jsx
│   │   ├── Navbar.jsx
│   │   └── ConfirmDialog.jsx
│   └── users/
│       └── UserFormModal.jsx   # Form crear/editar usuario
│
├── context/
│   └── AuthContext.jsx         # State global de autenticación
│
├── hooks/
│   └── useIdleTimeout.js       # Hook de inactividad
│
├── pages/
│   ├── LoginPage.jsx
│   ├── DashboardPage.jsx
│   └── UsersPage.jsx
│
├── services/
│   ├── api.js                  # Axios instance + interceptors
│   ├── authService.js          # Login, logout, verify
│   └── userService.js          # CRUD usuarios
│
├── utils/
│   └── errorMessages.js        # Helper de errores amigables
│
├── App.jsx                     # Routing principal
└── main.jsx                    # Entry point
```

---

## Convenciones de Código

### Backend (Python)

#### Estilo

```python
# Seguir PEP 8
# Usar black para formatear
black apps/

# Usar flake8 para linting
flake8 apps/

# Imports ordenados con isort
isort apps/
```

#### Docstrings

```python
def create_user(username, email, password):
    """
    Crea un nuevo usuario en el sistema.
    
    Args:
        username (str): Nombre de usuario único
        email (str): Email del usuario
        password (str): Contraseña en texto plano
    
    Returns:
        User: Instancia del usuario creado
    
    Raises:
        ValidationError: Si los datos son inválidos
        PermissionDenied: Si el usuario no tiene permisos
    """
    pass
```

#### Nombres

```python
# Variables y funciones: snake_case
user_count = 10
def get_active_users():
    pass

# Clases: PascalCase
class UserService:
    pass

# Constantes: UPPER_SNAKE_CASE
MAX_LOGIN_ATTEMPTS = 5
```

---

### Frontend (JavaScript/React)

#### Estilo

```javascript
// Usar ESLint
npm run lint

// Configuración en .eslintrc
```

#### Componentes

```javascript
/**
 * UserCard - Muestra información de un usuario
 * 
 * @param {Object} props
 * @param {Object} props.user - Datos del usuario
 * @param {Function} props.onEdit - Callback al editar
 */
const UserCard = ({ user, onEdit }) => {
  return (
    <div className="card">
      {/* ... */}
    </div>
  );
};
```

#### Nombres

```javascript
// Componentes: PascalCase
const UserList = () => {};

// Variables y funciones: camelCase
const userCount = 10;
const getActiveUsers = () => {};

// Constantes: UPPER_SNAKE_CASE
const MAX_RETRIES = 3;

// Archivos: camelCase
userService.js
authService.js

// Componentes archivo: PascalCase
UserCard.jsx
LoginForm.jsx
```

---

## Agregar Nuevas Funcionalidades

### Ejemplo: Agregar campo "Bio" a UserProfile

#### 1. Backend - Modelo

```python
# apps/users/domain/models.py

class UserProfile(TimestampedModel, SoftDeleteModel):
    # ... campos existentes ...
    bio = models.TextField(blank=True, null=True)  # ← NUEVO
```

#### 2. Backend - Migración

```bash
make makemigrations
make migrate
```

#### 3. Backend - Serializer

```python
# apps/users/api/serializers.py

class UserSerializer(serializers.ModelSerializer):
    # ... campos existentes ...
    bio = serializers.CharField(source='profile.bio', required=False)  # ← NUEVO
    
    class Meta:
        fields = [..., 'bio']  # ← AGREGAR

class UserUpdateSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(required=False, allow_blank=True)  # ← NUEVO
    
    def update(self, instance, validated_data):
        bio = validated_data.pop('bio', None)
        # ... lógica existente ...
        if bio is not None:
            instance.profile.bio = bio
            instance.profile.save()
```

#### 4. Frontend - Formulario

```javascript
// components/users/UserFormModal.jsx

<div>
  <label htmlFor="bio" className="label">
    Biografía
  </label>
  <textarea
    id="bio"
    rows={4}
    className="input"
    {...register('bio')}
    placeholder="Cuéntanos sobre ti..."
  />
</div>
```

#### 5. Frontend - Vista

```javascript
// pages/DashboardPage.jsx

<div>
  <dt className="text-sm font-medium text-gray-500">Biografía</dt>
  <dd className="text-sm text-gray-900">{user?.profile?.bio || 'Sin biografía'}</dd>
</div>
```

---

### Ejemplo: Agregar nuevo endpoint

#### Backend

```python
# apps/users/api/views.py

class UserViewSet(viewsets.ModelViewSet):
    # ... código existente ...
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """
        Resetea el password de un usuario (admin only).
        
        POST /api/users/{id}/reset_password/
        """
        user = self.get_object()
        
        # Generar password temporal
        temp_password = User.objects.make_random_password()
        user.set_password(temp_password)
        user.save()
        
        # Enviar email
        send_mail(
            'Password Reset',
            f'Tu nuevo password temporal es: {temp_password}',
            'noreply@example.com',
            [user.email],
        )
        
        return Response({
            'detail': 'Password reseteado. Email enviado al usuario.'
        })
```

#### Frontend

```javascript
// services/userService.js

const userService = {
  // ... métodos existentes ...
  
  async resetPassword(userId) {
    const response = await api.post(`/users/${userId}/reset_password/`);
    return response.data;
  },
};
```

```javascript
// pages/UsersPage.jsx

const handleResetPassword = async (userId, username) => {
  if (!confirm(`¿Resetear password de ${username}?`)) return;
  
  try {
    await userService.resetPassword(userId);
    toast.success('Password reseteado. Email enviado.');
  } catch (err) {
    toast.error('Error al resetear password');
  }
};
```

---

## Debugging

### Backend

#### Django Shell

```bash
# Acceder al shell
make shell-backend

# O manualmente
docker exec -it minimum_api_backend python manage.py shell

# Dentro del shell:
from django.contrib.auth.models import User
from apps.users.domain.models import UserProfile

# Ver todos los usuarios
User.objects.all()

# Crear usuario de prueba
user = User.objects.create_user('testuser', 'test@example.com', 'pass123')

# Ver profile
user.profile

# Ver permisos
user.user_permissions.all()
user.groups.all()
```

#### Logs

```bash
# Ver logs del backend
make logs-backend

# O con docker-compose
docker-compose logs -f backend

# Filtrar por error
docker-compose logs backend | grep ERROR
```

#### Debugger (pdb)

```python
# Agregar breakpoint en código
import pdb; pdb.set_trace()

# O en Python 3.7+
breakpoint()

# Comandos útiles en pdb:
# n - siguiente línea
# s - step into función
# c - continuar hasta próximo breakpoint
# p variable - imprimir variable
# q - quit
```

---

### Frontend

#### React DevTools

1. Instalar extensión de Chrome/Firefox
2. Abrir DevTools (F12)
3. Tab "Components" para ver árbol de componentes
4. Tab "Profiler" para performance

#### Console Logs

```javascript
// Logging estructurado
console.log('Usuario creado:', user);
console.error('Error al guardar:', error);
console.table(users);  // Ver array como tabla

// Condicional (solo en dev)
if (import.meta.env.DEV) {
  console.log('Debug info:', data);
}
```

#### Network

1. Abrir DevTools → Tab Network
2. Filtrar por XHR/Fetch
3. Ver requests a API
4. Inspeccionar headers, payload, response

---

## Best Practices

### Backend

#### 1. Usar Serializers diferentes para Read/Write

```python
# ❌ Malo
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    # Mezcla concerns

# ✅ Bueno
class UserSerializer(serializers.ModelSerializer):
    """Solo lectura"""
    pass

class UserCreateSerializer(serializers.ModelSerializer):
    """Solo escritura"""
    password = serializers.CharField(write_only=True)
```

#### 2. Validar en múltiples niveles

```python
# Serializer: Validación de formato
class UserSerializer:
    email = EmailField(required=True)

# Service: Validación de negocio
class UserService:
    def create_user(self, data):
        if User.objects.filter(email=data['email']).exists():
            raise ValidationError("Email ya existe")
```

#### 3. Usar select_related y prefetch_related

```python
# ❌ Malo (N+1 queries)
users = User.objects.all()
for user in users:
    print(user.profile.department)  # Query por cada user

# ✅ Bueno (1 query)
users = User.objects.select_related('profile').all()
for user in users:
    print(user.profile.department)
```

#### 4. Usar transacciones para operaciones complejas

```python
from django.db import transaction

@transaction.atomic
def transfer_ownership(from_user, to_user):
    from_user.items.all().update(owner=to_user)
    from_user.is_active = False
    from_user.save()
    # Si algo falla, se hace rollback automático
```

---

### Frontend

#### 1. Separar lógica de presentación

```javascript
// ❌ Malo
const UsersPage = () => {
  const [users, setUsers] = useState([]);
  // Mucha lógica + UI en un componente
};

// ✅ Bueno
const UsersPage = () => {
  const { users, loading, error, loadUsers } = useUsers();  // Hook custom
  return <UsersList users={users} />;  // Componente presentacional
};
```

#### 2. Usar Context para state global, props para local

```javascript
// ❌ Malo - prop drilling
<App>
  <Page user={user}>
    <Component user={user}>
      <DeepComponent user={user} />  // 😢
    </Component>
  </Page>
</App>

// ✅ Bueno - Context
const { user } = useAuth();  // En cualquier componente
```

#### 3. Memoizar componentes costosos

```javascript
import { memo } from 'react';

// Componente pesado
const UserCard = memo(({ user }) => {
  // Render pesado
});

// Solo re-renderiza si user cambia
```

#### 4. Cleanup en useEffect

```javascript
useEffect(() => {
  const timeout = setTimeout(() => {
    // Algo...
  }, 1000);
  
  // ✅ Cleanup
  return () => clearTimeout(timeout);
}, []);
```

---

## Testing

Ver [Testing Guide](TESTING.md) para detalles completos.

```bash
# Tests backend
make test

# Tests frontend
make test-frontend

# Coverage
make test-coverage
```

---

## Git Workflow

### Branching

```bash
# Feature
git checkout -b feature/add-user-bio

# Bugfix
git checkout -b fix/user-creation-error

# Hotfix
git checkout -b hotfix/security-patch
```

### Commits

```bash
# Formato: tipo(scope): descripción

git commit -m "feat(users): agregar campo bio a UserProfile"
git commit -m "fix(auth): corregir auto-refresh de JWT"
git commit -m "docs(api): actualizar documentación de endpoints"
git commit -m "test(users): agregar tests de UserService"
```

**Tipos**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

---

## Recursos

- **Django**: https://docs.djangoproject.com/
- **DRF**: https://www.django-rest-framework.org/
- **React**: https://react.dev/
- **Tailwind**: https://tailwindcss.com/docs

---

**¿Preguntas?** Abre un Issue o PR en GitHub.
