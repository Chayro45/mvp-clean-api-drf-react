# 📚 Lessons Learned - Aprendizajes del Proyecto

Este documento captura los conceptos aprendidos, decisiones tomadas y lecciones valiosas del proyecto Minimum API.

---

## 🎯 Objetivo del Proyecto

Aprender y demostrar **arquitectura limpia pragmática** con Django + React, simulando la estructura modular de microservicios sin su complejidad operacional, para proyectos de pequeña a mediana escala.

---

## 🏗️ Conceptos de Arquitectura

### 1. Arquitectura Limpia Pragmática

**Lo aprendido:**
- ✅ La arquitectura limpia no es todo o nada
- ✅ Se puede adaptar a las necesidades reales del proyecto
- ✅ Separación de capas aporta valor incluso sin purismo extremo

**Aplicado en el proyecto:**
```
API Layer (Views) → Application (Services) → Domain (Models) → Infrastructure (Cache)
```

**Lección clave:** *"Pragmatismo > Purismo"*

No implementamos:
- ❌ Repositorios abstractos (usamos Django ORM directamente)
- ❌ Puertos y adaptadores estrictos
- ❌ DTOs entre todas las capas

**Por qué:** Over-engineering para un proyecto de este tamaño. El ORM de Django ya es una abstracción suficiente.

---

### 2. Monolito Modular vs Microservicios

**Lo aprendido:**
- Un monolito bien estructurado es mejor que microservicios prematuros
- Apps Django desacopladas simulan la estructura de microservicios
- Extraer servicios más adelante es posible si la separación es clara

**Estructura aplicada:**
```
apps/
├── core/      # Compartido (NO es microservicio)
├── auth/      # Podría ser servicio independiente
└── users/     # Podría ser servicio independiente
```

**Regla aplicada:** Una app NO puede importar de otra (excepto `core`)

**Lección clave:** *"Start monolith, split when needed"*

---

### 3. Service Layer

**Cuándo usar Services:**
- ✅ Lógica que involucra múltiples modelos
- ✅ Validaciones de negocio complejas
- ✅ Operaciones transaccionales
- ❌ CRUD simple (dejarlo en serializers)

**Ejemplo del proyecto:**

```python
# UserService solo para lógica compleja
class UserService:
    def create_user(self, validated_data):
        # Validación de negocio: límite de usuarios
        if User.objects.filter(is_active=True).count() >= MAX_USERS:
            raise ValidationError("Límite alcanzado")
        
        # Múltiples operaciones
        user = User.objects.create_user(...)
        self._send_welcome_email(user)
        self._invalidate_cache()
        return user
```

**Lección clave:** *"Services solo cuando aportan valor, no por dogma"*

---

## 🔐 Autenticación y Seguridad

### 1. JWT con Refresh Tokens

**Lo aprendido:**
- JWT es stateless y escala bien
- Refresh tokens permiten revocar acceso sin perder stateless
- Auto-refresh transparente mejora UX dramáticamente

**Implementación:**
```
Access Token:  Corta duración (30 min prod, 2 min dev)
Refresh Token: Larga duración (7 días prod, 15 min dev)
Blacklist:     En Redis para revocar refresh tokens
```

**Flujo de Auto-refresh:**
```
1. Request con access expirado (401)
2. Interceptor detecta 401
3. Refresh automático con refresh token
4. Nuevo access token
5. Reintenta request original
6. Usuario NO se entera (transparente)
```

**Lección clave:** *"Auto-refresh es crítico para UX en SPAs"*

---

### 2. Sistema de Permisos Nativo de Django

**Decisión:** Usar sistema nativo en lugar de custom

**Ventajas experimentadas:**
- ✅ Integrado con Django Admin
- ✅ Bien documentado y testeado
- ✅ Suficiente para 90% de casos
- ✅ Compatible con todo el ecosistema

**Estructura aplicada:**
```
User → Groups (roles) → Permissions
```

**Cache de permisos:**
```python
# Key pattern en Redis
user_permissions:{user_id}

# TTL: 1 hora
# Invalidación: Manual al cambiar grupos
```

**Lección clave:** *"Usa lo que ya existe antes de crear custom"*

---

### 3. Detección de Inactividad

**Implementado:**
- 10 minutos de inactividad → Warning modal (60 seg countdown)
- Sin interacción → Logout automático
- Eventos monitoreados: mousedown, mousemove, keypress, scroll, touchstart

**Custom Hook:**
```javascript
const useIdleTimeout = ({ onIdle, idleTime }) => {
  // Resetea timer en cada evento
  // Llama onIdle al expirar
};
```

**Lección clave:** *"Seguridad vs UX es un balance fino"*

---

### 4. Sync Entre Tabs

**Problema:** Usuario hace logout en Tab 1, Tab 2 sigue "logueada"

**Solución:** localStorage events

```javascript
window.addEventListener('storage', (e) => {
  if (e.key === 'access_token' && !e.newValue) {
    // Otra tab hizo logout
    logout();
    navigate('/login');
  }
});
```

**Lección clave:** *"localStorage events son perfectos para sync entre tabs"*

---

## 🗄️ Base de Datos y Modelos

### 1. User Model: OneToOne vs Custom User

**Decisión:** UserProfile con OneToOne a User nativo

**Pros:**
- ✅ Pragmático y rápido de implementar
- ✅ Compatible con todo el ecosistema Django
- ✅ No requiere migraciones complejas

**Cons:**
- ❌ Dos queries para datos completos (mitigable con select_related)
- ❌ Menos "limpio" que custom user model

**Cuándo usar qué:**
- **OneToOne**: Proyectos existentes, prototipado rápido
- **Custom User**: Proyectos nuevos (greenfield)

**Lección clave:** *"OneToOne es perfectamente válido si el contexto lo justifica"*

---

### 2. Soft Delete Pattern

**Implementación:**
```python
class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def delete(self):
        self.deleted_at = timezone.now()
        self.save()
    
    def restore(self):
        self.deleted_at = None
        self.save()
```

**Ventajas:**
- ✅ Auditoría completa
- ✅ Recuperación de datos
- ✅ Cumplimiento legal (GDPR)

**Desventajas:**
- ❌ Queries más complejas (filter deleted_at__isnull=True)
- ❌ DB crece con el tiempo

**Lección clave:** *"Soft delete es esencial para auditoría y compliance"*

---

### 3. Signals de Django

**Uso:** Crear UserProfile automáticamente al crear User

```python
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
```

**Ventajas:**
- ✅ Automático y consistente
- ✅ Desacoplado del código de creación

**Desventajas:**
- ❌ "Magia" (difícil de debuggear)
- ❌ Problemas en tests si no se maneja bien

**Lección clave:** *"Signals para lógica automática simple, no para orquestación compleja"*

---

## ⚡ Performance y Cache

### 1. Cache con Redis

**Uso en el proyecto:** Permisos de usuario

**Patrón:** Cache-Aside (Lazy Loading)

```python
def get_user_permissions(user_id):
    # 1. Intentar cache
    cached = cache.get(f'user_permissions:{user_id}')
    if cached:
        return cached
    
    # 2. Si no existe, calcular
    permissions = calculate_permissions(user_id)
    
    # 3. Guardar en cache
    cache.set(f'user_permissions:{user_id}', permissions, timeout=3600)
    
    return permissions
```

**Invalidación:**
```python
# Manual al cambiar grupos/permisos
def invalidate_user_permissions_cache(user_id):
    cache.delete(f'user_permissions:{user_id}')
```

**Métricas observadas:**
- Consulta sin cache: ~50ms
- Consulta con cache: ~2ms
- Mejora: ~25x más rápido

**Lección clave:** *"Cache-Aside es simple y efectivo para datos que no cambian frecuentemente"*

---

### 2. N+1 Queries

**Problema detectado:**
```python
# ❌ Malo (N+1 queries)
users = User.objects.all()
for user in users:
    print(user.profile.department)  # 1 query por user
```

**Solución:**
```python
# ✅ Bueno (2 queries total)
users = User.objects.select_related('profile').all()
for user in users:
    print(user.profile.department)  # Sin queries extra
```

**Lección clave:** *"Django Debug Toolbar es tu amigo para detectar N+1"*

---

## 🎨 Frontend

### 1. Context API vs Redux

**Decisión:** Context API

**Razones:**
- Proyecto pequeño-mediano
- Menos boilerplate
- Hooks nativos de React

**Cuándo usar Redux:**
- Apps con state muy complejo
- Muchas actualizaciones concurrentes
- Necesidad de time-travel debugging

**Implementado:**
```javascript
<AuthProvider>
  <App />
</AuthProvider>

// En cualquier componente:
const { user, login, logout } = useAuth();
```

**Lección clave:** *"Context API es suficiente para la mayoría de casos"*

---

### 2. Custom Hooks

**Ejemplo: useIdleTimeout**

```javascript
const useIdleTimeout = ({ onIdle, idleTime }) => {
  useEffect(() => {
    // Lógica de detección
  }, []);
  
  return { resetTimer };
};
```

**Ventajas:**
- ✅ Lógica reutilizable
- ✅ Fácil de testear
- ✅ Composable

**Lección clave:** *"Extract hooks cuando la lógica se repite o es compleja"*

---

### 3. Protected Routes

**Patrón implementado:**

```javascript
<Route path="/users" element={
  <ProtectedRoute permission="auth.view_user">
    <UsersPage />
  </ProtectedRoute>
} />
```

**Con permisos granulares:**
```javascript
if (permission && !hasPermission(permission)) {
  return <Forbidden />;
}
```

**Lección clave:** *"HOCs son perfectos para auth guards"*

---

### 4. Axios Interceptors

**Auto-refresh transparente:**

```javascript
api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      // Auto-refresh logic
      const newToken = await refreshToken();
      error.config.headers.Authorization = `Bearer ${newToken}`;
      return api(error.config);  // Retry
    }
    return Promise.reject(error);
  }
);
```

**Lección clave:** *"Interceptors son el lugar correcto para lógica global de HTTP"*

---

## 🐛 Problemas Encontrados y Soluciones

### 1. Create User retornaba dict en lugar de objeto

**Problema:**
```python
def create(self, request):
    user = service.create_user(data)  # Retorna dict
    serializer = UserSerializer(user)  # Error: dict no tiene atributos
```

**Solución:**
```python
def create(self, request):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()  # Retorna objeto User
    return Response(UserSerializer(user).data)
```

**Lección:** *"Serializer.save() retorna la instancia, no dict"*

---

### 2. Checkboxes de roles no funcionaban

**Problema:** react-hook-form no maneja checkboxes múltiples automáticamente

**Solución:**
```javascript
<input
  type="checkbox"
  value={group.id}
  {...register('group_ids')}
  onChange={(e) => {
    const currentValues = watch('group_ids') || [];
    const value = parseInt(e.target.value);
    const newValues = e.target.checked
      ? [...currentValues, value]
      : currentValues.filter(id => id !== value);
    setValue('group_ids', newValues);
  }}
  checked={watch('group_ids')?.includes(group.id)}
/>
```

**Lección:** *"react-hook-form requiere manejo custom para checkboxes"*

---

### 3. Rutas del router capturaban /groups/

**Problema:**
```python
urlpatterns = [
    path('', include(router.urls)),  # Captura primero
    path('groups/', ...),             # Nunca llega aquí
]
```

**Solución:**
```python
urlpatterns = [
    path('groups/', ...),             # Rutas específicas primero
    path('', include(router.urls)),  # Router al final
]
```

**Lección:** *"Django procesa URLs en orden secuencial"*

---

## 💡 Decisiones Técnicas Clave

### 1. Docker Compose para Desarrollo

**Por qué:**
- ✅ Consistencia entre entornos
- ✅ Setup en minutos
- ✅ Servicios aislados

**Aprendido:**
- Usar volúmenes para hot-reload
- depends_on con healthchecks
- Networks para comunicación inter-servicios

---

### 2. Management Commands

**Ventaja:** Automatización de tareas administrativas

**Implementados:**
- `seed_roles` - Crear grupos y permisos
- `createsuperuser_auto` - Superuser automático
- `wait_for_db` - Esperar PostgreSQL

**Lección:** *"Management commands son mejores que scripts bash sueltos"*

---

### 3. Throttling y Rate Limiting

**Implementado:**
- Login: 5 requests/minuto
- API autenticada: 1000 requests/hora
- API anónima: 100 requests/hora

**Herramienta:** DRF Throttling

**Lección:** *"Rate limiting es esencial contra brute force y abuse"*

---

## 🚀 Lo Que Funcionó Muy Bien

1. **Arquitectura en capas** - Código organizado y mantenible
2. **JWT con auto-refresh** - UX transparente
3. **Docker Compose** - Setup instantáneo
4. **Swagger automático** - Documentación siempre actualizada
5. **Makefile** - Comandos consistentes
6. **React Hook Form** - Validaciones robustas
7. **Tailwind CSS** - Desarrollo UI rápido
8. **Context API** - State management simple

---

## ⚠️ Lo Que Se Podría Mejorar

1. **Tests** - Coverage bajo (solo ejemplos básicos)
2. **Error boundaries** - Frontend crashea sin recovery
3. **Logging** - Logs no estructurados
4. **Monitoring** - Sin métricas de performance
5. **CI/CD** - Pipeline básico, podría ser más robusto
6. **i18n** - Solo en español
7. **Accessibilidad** - No testeada con lectores de pantalla

---

## 📊 Métricas del Proyecto

**Backend:**
- Líneas de código: ~3,500
- Apps: 3 (core, users, auth)
- Modelos: 1 custom (UserProfile)
- Endpoints: 15
- Tests: 5 básicos

**Frontend:**
- Líneas de código: ~2,000
- Componentes: 12
- Páginas: 3
- Services: 3
- Hooks custom: 1

**Infraestructura:**
- Contenedores Docker: 4
- Base de datos: PostgreSQL
- Cache: Redis
- Tiempo de setup: <10 minutos

---

## 🎓 Conclusiones Finales

### Para Proyectos Reales

**✅ Aplicar:**
- Arquitectura en capas clara
- Auto-refresh de JWT
- Cache estratégico
- Soft delete
- Management commands
- Docker para consistencia

**⚠️ Adaptar:**
- Service layer (solo si es necesario)
- Custom hooks (extraer cuando hay repetición)
- Context vs Redux (según tamaño)

**❌ Evitar:**
- Over-engineering prematuro
- Microservicios sin necesidad
- Cache de todo sin medición
- Signals complejos

---

### Aprendizajes Personales

1. **Arquitectura limpia** no es blanco o negro, hay grises pragmáticos
2. **JWT con auto-refresh** es la combinación perfecta para SPAs
3. **Docker** elimina el "funciona en mi máquina"
4. **Management commands** son subestimados pero muy poderosos
5. **Cache** es fácil de agregar, difícil de invalidar correctamente
6. **React hooks** cambiaron el juego de React
7. **Tailwind** es más productivo que CSS custom para proyectos rápidos
8. **Documentación** es tan importante como el código

---

### Si Empezara de Nuevo

**Haría igual:**
- Arquitectura en capas
- Django + DRF + React
- Docker Compose
- JWT con auto-refresh

**Cambiaría:**
- Más tests desde el inicio (TDD)
- Logging estructurado desde día 1
- Error boundaries en frontend
- Monitoreo básico (Prometheus)
- i18n desde el principio

---

## 🔗 Recursos que Ayudaron

**Arquitectura:**
- Clean Architecture (Robert C. Martin)
- Pragmatic Programmer (Hunt & Thomas)

**Django:**
- Django for APIs (William S. Vincent)
- Django REST Framework docs
- Two Scoops of Django

**React:**
- React docs oficiales
- Kent C. Dodds blog
- Epic React

**DevOps:**
- Docker docs
- 12 Factor App

---

## 💬 Reflexión Final

Este proyecto demuestra que es posible crear aplicaciones modernas, mantenibles y bien arquitecturadas sin caer en over-engineering.

La clave está en:
1. Entender los principios
2. Adaptarlos al contexto
3. Priorizar pragmatismo
4. Documentar decisiones

**El mejor código es el que resuelve el problema de forma simple y mantenible.**

---

¿Preguntas? ¿Feedback? Abre un Issue en GitHub o contáctame directamente.
