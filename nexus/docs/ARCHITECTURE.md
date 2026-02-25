# 🏗️ Arquitectura del Proyecto

## Tabla de Contenidos

- [Visión General](#visión-general)
- [Principios de Diseño](#principios-de-diseño)
- [Arquitectura Backend](#arquitectura-backend)
- [Arquitectura Frontend](#arquitectura-frontend)
- [Flujo de Datos](#flujo-de-datos)
- [Decisiones Técnicas](#decisiones-técnicas)
- [Patrones Implementados](#patrones-implementados)

---

## Visión General

Minimum API implementa una **arquitectura limpia pragmática**, balanceando principios teóricos con simplicidad práctica. El proyecto está estructurado para simular microservicios dentro de un monolito, permitiendo aprendizaje sin complejidad operacional.

### Filosofía

```
Pragmatismo > Purismo
Simplicidad > Complejidad
Educación > Producción extrema
```

No seguimos clean architecture al pie de la letra, sino que tomamos sus mejores ideas adaptándolas a un proyecto real y mantenible.

---

## Principios de Diseño

### 1. Separación de Responsabilidades

Cada capa tiene una responsabilidad clara:

```
┌─────────────────────────────────────┐
│  API Layer (Views/Serializers)     │  ← HTTP, Validación de entrada
├─────────────────────────────────────┤
│  Application Layer (Services)      │  ← Lógica de negocio
├─────────────────────────────────────┤
│  Domain Layer (Models)             │  ← Entidades del negocio
├─────────────────────────────────────┤
│  Infrastructure (Cache/External)   │  ← Servicios externos
└─────────────────────────────────────┘
```

### 2. Apps Desacopladas

Cada app Django es autónoma y podría extraerse como microservicio:

```
apps/
├── core/        → Funcionalidad compartida (no es un microservicio)
├── auth/        → Autenticación y autorización
└── users/       → Gestión de usuarios y perfiles
```

**Regla**: Una app NO puede importar directamente de otra app (excepto de `core`).

### 3. Dependencia hacia adentro

```
API Layer → depende de → Application Layer
Application Layer → depende de → Domain Layer
Domain Layer → NO depende de nadie (excepto Django ORM)
```

---

## Arquitectura Backend

### Estructura de Capas

#### 1. **API Layer** (`api/`)

**Responsabilidad**: Manejo de HTTP, serialización, validación de entrada.

```python
# apps/users/api/views.py
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet maneja:
    - Routing automático
    - Validación de permisos
    - Delegación a services
    """
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # Serializer llama al service
        return Response(UserSerializer(user).data)
```

**Componentes**:
- `views.py`: ViewSets (CRUD + actions custom)
- `serializers.py`: Read/Write serializers separados
- `urls.py`: Routing

**Patrones**:
- ViewSets de DRF para CRUD automático
- Serializers diferentes para lectura y escritura
- Actions custom con decorador `@action`

---

#### 2. **Application Layer** (`application/`)

**Responsabilidad**: Lógica de negocio, orquestación, validaciones complejas.

```python
# apps/users/application/services.py
class UserService:
    """
    Service encapsula lógica de negocio:
    - Validaciones complejas
    - Orquestación de múltiples operaciones
    - No sabe nada de HTTP
    """
    def create_user(self, validated_data):
        # Validación de negocio
        if User.objects.filter(is_active=True).count() >= MAX_USERS:
            raise ValidationError("Límite alcanzado")
        
        # Lógica compleja
        user = User.objects.create_user(...)
        self._send_welcome_email(user)
        self._invalidate_cache()
        
        return user
```

**Cuándo usar Services**:
- ✅ Lógica que involucra múltiples modelos
- ✅ Validaciones de negocio complejas
- ✅ Operaciones que requieren transacciones
- ❌ CRUD simple (dejar en serializer)

---

#### 3. **Domain Layer** (`domain/`)

**Responsabilidad**: Modelos de negocio, entidades, reglas del dominio.

```python
# apps/users/domain/models.py
class UserProfile(TimestampedModel, SoftDeleteModel):
    """
    Modelo del dominio:
    - Define entidad del negocio
    - Propiedades y métodos del dominio
    - NO sabe de HTTP ni de services
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    
    @property
    def full_name(self):
        """Lógica del dominio"""
        return f"{self.user.first_name} {self.user.last_name}".strip()
```

**Componentes**:
- `models.py`: Modelos Django (entidades)
- Signals para lógica automática (ej: crear profile al crear user)

---

#### 4. **Infrastructure Layer** (`infrastructure/`)

**Responsabilidad**: Integración con servicios externos (Redis, S3, APIs externas).

```python
# apps/users/infrastructure/cache.py
class UserPermissionCache:
    """
    Abstracción de Redis:
    - Encapsula lógica de cache
    - Podría cambiarse por Memcached sin afectar otras capas
    """
    def get(self, user_id):
        return cache.get(f'user_permissions:{user_id}')
    
    def set(self, user_id, permissions):
        cache.set(f'user_permissions:{user_id}', permissions, timeout=3600)
```

---

### ¿Por qué esta estructura?

#### Ventajas:
1. **Testeable**: Cada capa se puede testear independientemente
2. **Mantenible**: Cambios aislados (ej: cambiar cache Redis → Memcached)
3. **Escalable**: Apps pueden extraerse como microservicios
4. **Educativa**: Clara separación de responsabilidades

#### Pragmatismo:
- No usamos puertos/adaptadores estrictos (over-engineering)
- Usamos Django ORM directamente (no repositorios abstractos)
- Services solo cuando aportan valor (no por dogma)

---

## Arquitectura Frontend

### Estructura

```
src/
├── components/       → Componentes reutilizables
│   ├── auth/        → Específicos de autenticación
│   ├── common/      → Compartidos (Modal, Spinner, etc.)
│   └── users/       → Específicos de usuarios
├── context/         → State global (Context API)
├── hooks/           → Custom hooks
├── pages/           → Páginas completas (rutas)
├── services/        → Comunicación con API
└── utils/           → Utilidades y helpers
```

### Patrones Frontend

#### 1. **Context API para State Global**

```javascript
// context/AuthContext.jsx
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  
  const login = async (username, password) => {
    const data = await authService.login(username, password);
    setUser(data.user);
  };
  
  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
```

**Por qué Context API y no Redux**:
- Proyecto pequeño-mediano
- Menos boilerplate
- Hooks nativos de React
- Suficiente para este caso de uso

---

#### 2. **Services Layer (Frontend)**

```javascript
// services/userService.js
const userService = {
  async getUsers(params) {
    const response = await api.get('/users/', { params });
    return response.data;
  },
  
  async createUser(userData) {
    const response = await api.post('/users/', userData);
    return response.data;
  },
};
```

**Ventajas**:
- Encapsula comunicación con API
- Reutilizable en cualquier componente
- Fácil de mockear en tests

---

#### 3. **Protected Routes**

```javascript
// components/auth/ProtectedRoute.jsx
const ProtectedRoute = ({ children, permission }) => {
  const { user, hasPermission } = useAuth();
  
  if (!user) return <Navigate to="/login" />;
  if (permission && !hasPermission(permission)) return <Forbidden />;
  
  return children;
};
```

---

## Flujo de Datos

### Flujo de Autenticación

```
┌─────────┐
│ Usuario │
└────┬────┘
     │ 1. Login (username, password)
     ▼
┌─────────────┐
│ LoginForm   │
└──────┬──────┘
       │ 2. login(username, password)
       ▼
┌──────────────┐
│ AuthContext  │
└──────┬───────┘
       │ 3. authService.login()
       ▼
┌──────────────┐
│ Axios (API)  │────────┐
└──────┬───────┘        │ 4. POST /api/auth/login/
       │                │
       │ ◄──────────────┘ 5. { access, refresh, user }
       │
       │ 6. localStorage.setItem('access_token', ...)
       │ 7. setUser(userData)
       │
       └──────► Dashboard
```

---

### Flujo de Auto-Refresh JWT

```
Usuario hace request
     │
     ▼
┌─────────────────┐
│ api.get('/...') │
└────────┬────────┘
         │ + Authorization: Bearer <access_token>
         ▼
    Backend valida token
         │
    ┌────┴────┐
    │         │
  VÁLIDO   EXPIRADO (401)
    │         │
    ▼         ▼
 Retorna  Interceptor detecta 401
  datos        │
               │ POST /api/auth/refresh/
               │ { refresh: <refresh_token> }
               ▼
          Backend valida refresh
               │
          ┌────┴────┐
          │         │
       VÁLIDO   EXPIRADO
          │         │
          │         └──► Logout + Redirect /login
          │
          ▼ Nuevo access token
     localStorage.setItem(...)
          │
          └──► Reintenta request original
                    │
                    ▼
                 Success
```

**Transparente para el usuario**: No se entera de que el token se renovó.

---

### Flujo CRUD de Usuario

```
1. Usuario hace click "Crear Usuario"
     ↓
2. Modal se abre (UserFormModal)
     ↓
3. Usuario llena formulario
     ↓
4. Submit → react-hook-form valida
     ↓
5. userService.createUser(data)
     ↓
6. Axios POST /api/users/
     │
     ├─ Interceptor agrega JWT
     │
     └─► Backend recibe request
           │
           ├─ JWTAuthentication valida token
           ├─ IsAuthenticated verifica auth
           ├─ HasPermission('auth.add_user') verifica permiso
           │
           └─► UserViewSet.create()
                 │
                 ├─ UserCreateSerializer valida datos
                 │
                 └─► Serializer.save()
                       │
                       ├─ User.objects.create_user(...)
                       ├─ Signal crea UserProfile automáticamente
                       ├─ Cache se invalida
                       │
                       └─► Retorna UserSerializer(user).data
                             │
     ◄───────────────────────┘
     │
7. Frontend recibe usuario creado
     │
8. Toast "Usuario creado exitosamente"
     │
9. Modal se cierra
     │
10. Lista se recarga con el nuevo usuario
```

---

## Decisiones Técnicas

### 1. User Model: OneToOne vs Custom User

**Decisión**: UserProfile con OneToOne a User nativo de Django

**Razones**:
- ✅ Pragmático para proyectos existentes
- ✅ Compatible con todo el ecosistema Django
- ✅ No requiere migraciones complejas
- ✅ Educativo (muestra patrón común)
- ❌ Custom User sería mejor para greenfield

**Trade-off aceptado**: Dos queries para datos completos del usuario (optimizable con select_related).

---

### 2. JWT: Stateless vs Session-based

**Decisión**: JWT con refresh tokens

**Razones**:
- ✅ Stateless (escala horizontalmente)
- ✅ Funciona bien con SPA
- ✅ Refresh token permite revocar acceso
- ✅ Educativo (patrón moderno)

**Trade-off**: Blacklist de refresh tokens requiere Redis.

---

### 3. Cache: Redis vs Memcached

**Decisión**: Redis

**Razones**:
- ✅ Estructuras de datos ricas
- ✅ Persistencia (opcional)
- ✅ Pub/Sub (para futuro)
- ✅ Más popular en ecosistema Django

---

### 4. Frontend State: Context API vs Redux

**Decisión**: Context API

**Razones**:
- ✅ Proyecto pequeño-mediano
- ✅ Menos boilerplate
- ✅ Hooks nativos
- ✅ Suficiente para este caso

**Cuándo Redux**: Apps con state muy complejo o muchas actualizaciones concurrentes.

---

## Patrones Implementados

### Backend

1. **ViewSet Pattern**: CRUD automático con DRF
2. **Service Layer**: Lógica de negocio aislada
3. **Repository Pattern (implícito)**: Django ORM como repositorio
4. **Cache-Aside Pattern**: Lazy loading con Redis
5. **Soft Delete Pattern**: Auditoría sin pérdida de datos
6. **Signal Pattern**: Reacciones automáticas a eventos del modelo
7. **Management Command Pattern**: Scripts reutilizables

### Frontend

1. **Container/Presenter Pattern**: Páginas (containers) + Componentes (presenters)
2. **Custom Hooks**: Lógica reutilizable (useIdleTimeout)
3. **Higher-Order Component**: ProtectedRoute
4. **Service Layer**: Encapsulación de API calls
5. **Context Provider Pattern**: State global
6. **Controlled Components**: Formularios con react-hook-form

---

## Escalabilidad Futura

### Camino a Microservicios Reales

Si el proyecto creciera, así se extraerían servicios:

```
1. Extraer apps/auth → Auth Service
   - API Gateway maneja autenticación
   - JWT compartido entre servicios

2. Extraer apps/users → Users Service
   - Eventos para sincronizar datos (RabbitMQ/Kafka)
   - API interna para consultas entre servicios

3. Comunicación
   - REST para cliente → servicio
   - gRPC para servicio → servicio (performance)
   - Eventos para eventual consistency
```

**Por ahora**: No necesitamos esta complejidad. El monolito modular es suficiente.

---

## Conclusión

Esta arquitectura balancea:
- **Teoría** (clean architecture)
- **Pragmatismo** (Django ORM, no over-engineering)
- **Educación** (patrones claros y documentados)
- **Mantenibilidad** (código simple y organizado)

No es perfecta, pero es **suficientemente buena** para aprender y para proyectos reales pequeños-medianos.

---

**Siguiente lectura recomendada**: [Development Guide](DEVELOPMENT.md)
