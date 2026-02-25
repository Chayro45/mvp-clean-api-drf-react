# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [Unreleased]

### Planeado
- Tests unitarios completos para todas las apps
- Tests E2E con Playwright
- Internacionalización (i18n)
- Dark mode en frontend
- WebSockets para notificaciones real-time
- Sistema de notificaciones in-app

---

## [1.0.0] - 2024-02-15

### 🎉 Release Inicial

Primera versión completa del proyecto educativo.

### Added - Backend

#### Core
- Sistema de modelos base (`BaseModel`, `TimestampedModel`, `SoftDeleteModel`)
- Helper de permisos con cache en Redis
- Health check endpoint (`/health/`)
- Management command `wait_for_db`

#### Users
- Modelo `UserProfile` con OneToOne a User nativo
- CRUD completo de usuarios
- Sistema de permisos basado en grupos (roles)
- Soft delete para usuarios
- Cache de permisos en Redis (TTL 1h)
- Endpoint de cambio de password
- Endpoint de listado de grupos
- Management commands:
  - `seed_roles` - Crear roles iniciales
  - `createsuperuser_auto` - Superuser automático para desarrollo

#### Auth
- Autenticación JWT con SimpleJWT
- Login endpoint con rate limiting (5/min)
- Token refresh con rotación
- Token blacklist en logout
- Verify token endpoint
- Current user endpoint (`/auth/me/`)

#### Features Generales
- Documentación automática con Swagger (drf-spectacular)
- Filtrado y búsqueda avanzada con django-filter
- Paginación en todos los endpoints de lista
- Throttling configurado (5/min login, 100/h anon, 1000/h auth)
- Logging mejorado
- CORS configurado
- Settings separados (base, dev, prod)

### Added - Frontend

#### Auth
- Página de login con validaciones
- Context API para state global de autenticación
- Auto-refresh transparente de JWT con Axios interceptors
- Detección de inactividad (10 min → modal 60 seg → logout)
- Sync entre tabs con localStorage events
- Protected routes con validación de permisos

#### Users
- Dashboard con información del usuario
- Lista de usuarios con paginación
- Búsqueda en tiempo real
- CRUD completo (crear, editar, inactivar)
- Modal de creación de usuario
- Modal de edición de usuario
- Selección múltiple de roles con checkboxes
- Validaciones con react-hook-form
- Manejo de errores amigables

#### Components
- Modal reutilizable
- LoadingSpinner con tamaños configurables
- Navbar con información de usuario
- ProtectedRoute HOC
- IdleWarningModal con countdown

#### Features Generales
- Tailwind CSS con clases custom
- Toast notifications (react-hot-toast)
- Routing con React Router v6
- Services layer para API calls
- Custom hook `useIdleTimeout`
- Manejo de errores centralizado

### Added - DevOps

- Docker Compose para desarrollo (4 servicios)
- Docker Compose para producción (con Nginx)
- Makefile con comandos útiles
- Script de backup automático de PostgreSQL
- GitHub Actions para CI/CD
- Configuración de Nginx con SSL
- Health checks en containers

### Added - Documentación

- README principal completo con screenshots
- ARCHITECTURE.md - Decisiones de arquitectura
- GETTING_STARTED.md - Guía de inicio rápido
- API_DOCUMENTATION.md - Documentación completa de endpoints
- DEVELOPMENT.md - Guía para desarrolladores
- TESTING.md - Guía de testing
- DEPLOYMENT.md - Guía de deployment (teórica)
- LESSONS_LEARNED.md - Aprendizajes del proyecto
- Backend README específico
- Frontend README específico
- CONTRIBUTING.md - Guía de contribución
- CHANGELOG.md - Este archivo

---

## [0.5.0] - 2024-02-10

### Added
- Backend básico con Django + DRF
- Frontend básico con React + Vite
- Autenticación JWT básica
- CRUD de usuarios sin frontend

### Changed
- Migración de Custom User a UserProfile (OneToOne)

---

## [0.1.0] - 2024-02-01

### Added
- Estructura inicial del proyecto
- Docker Compose básico
- Configuración inicial de Django
- Configuración inicial de React

---

## Tipos de Cambios

- `Added` - Nuevas funcionalidades
- `Changed` - Cambios en funcionalidades existentes
- `Deprecated` - Funcionalidades que serán removidas
- `Removed` - Funcionalidades removidas
- `Fixed` - Corrección de bugs
- `Security` - Vulnerabilidades o mejoras de seguridad

---

## Versionado

Usamos [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.x.x): Cambios incompatibles en el API
- **MINOR** (x.1.x): Nueva funcionalidad compatible con versiones anteriores
- **PATCH** (x.x.1): Corrección de bugs compatible con versiones anteriores

---

[unreleased]: https://github.com/tu-usuario/minimum-api/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/tu-usuario/minimum-api/releases/tag/v1.0.0
[0.5.0]: https://github.com/tu-usuario/minimum-api/releases/tag/v0.5.0
[0.1.0]: https://github.com/tu-usuario/minimum-api/releases/tag/v0.1.0
