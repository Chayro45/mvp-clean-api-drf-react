# 🚀 Minimum API - Arquitectura Limpia con Django + React

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

> Proyecto educativo de arquitectura limpia pragmática simulando microservicios con Django REST Framework y React.

---

## 📖 Tabla de Contenidos

- [Descripción](#-descripción)
- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Stack Tecnológico](#-stack-tecnológico)
- [Inicio Rápido](#-inicio-rápido)
- [Screenshots](#-screenshots)
- [Documentación](#-documentación)
- [Testing](#-testing)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

---

## 📝 Descripción

**Minimum API** es un proyecto educativo diseñado para aprender y demostrar buenas prácticas de desarrollo fullstack moderno, con énfasis en:

- **Arquitectura Limpia Pragmática**: Separación de capas sin sobre-ingeniería
- **Simulación de Microservicios**: Apps Django desacopladas que podrían extraerse como servicios independientes
- **Autenticación Robusta**: JWT con auto-refresh, detección de inactividad y sync entre tabs
- **Sistema de Permisos**: Control de acceso granular basado en roles
- **Performance**: Cache con Redis para optimizar consultas frecuentes
- **Developer Experience**: Docker Compose, hot-reload, Swagger UI

Este proyecto **NO** implementa microservicios reales (con comunicación inter-servicios), sino que simula su estructura modular dentro de un monolito, ideal para aprendizaje sin la complejidad operacional de una arquitectura distribuida.

---

## ✨ Características

### Backend
- ✅ Django REST Framework con ViewSets
- ✅ Autenticación JWT (access + refresh tokens)
- ✅ Auto-refresh transparente de tokens
- ✅ Sistema de permisos nativo de Django
- ✅ Cache de permisos en Redis
- ✅ Throttling y rate limiting
- ✅ Swagger UI automático (drf-spectacular)
- ✅ Soft delete para auditoría
- ✅ Management commands personalizados
- ✅ Arquitectura en capas (API → Application → Domain → Infrastructure)

### Frontend
- ✅ React 18 + Vite
- ✅ Context API para state management
- ✅ Protected routes con validación de permisos
- ✅ Auto-refresh de JWT con interceptores Axios
- ✅ Detección de inactividad (10 min)
- ✅ Sync entre tabs (localStorage events)
- ✅ Tailwind CSS con componentes reutilizables
- ✅ React Hook Form con validaciones
- ✅ Toast notifications (react-hot-toast)
- ✅ Modals y confirmaciones elegantes

### DevOps
- ✅ Docker Compose multi-servicio
- ✅ Hot-reload en desarrollo
- ✅ Scripts de backup automático
- ✅ Configuración para producción incluida
- ✅ GitHub Actions CI/CD
- ✅ Makefile con comandos útiles

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  React + Vite + Tailwind CSS                          │  │
│  │  • Context API (Auth)                                 │  │
│  │  • Protected Routes                                    │  │
│  │  • Axios Interceptors (Auto-refresh JWT)             │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                     BACKEND (Django)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   API       │  │   API       │  │   API       │         │
│  │  (Views)    │  │  (Views)    │  │  (Views)    │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                 │                 │                │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐         │
│  │ Application │  │ Application │  │ Application │         │
│  │ (Services)  │  │ (Services)  │  │ (Services)  │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                 │                 │                │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐         │
│  │   Domain    │  │   Domain    │  │   Domain    │         │
│  │  (Models)   │  │  (Models)   │  │  (Models)   │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                 │                 │                │
│  ┌──────▼───────────────┬─▼─────────────┬──▼──────┐        │
│  │ Infrastructure       │               │         │        │
│  │ • Cache (Redis)      │  PostgreSQL   │  Auth   │        │
│  └──────────────────────┴───────────────┴─────────┘        │
└─────────────────────────────────────────────────────────────┘

Apps Desacopladas (simulando microservicios):
  • apps/auth     → Autenticación y autorización
  • apps/users    → Gestión de usuarios y perfiles
  • apps/core     → Funcionalidad compartida
```

**Filosofía**: Cada app es autónoma y podría extraerse como microservicio independiente, pero conviven en un monolito para simplicidad operacional.

---

## 🛠️ Stack Tecnológico

### Backend
- **Python 3.12**
- **Django 4.2** - Framework web
- **Django REST Framework 3.15** - API REST
- **SimpleJWT** - Autenticación JWT
- **PostgreSQL 14** - Base de datos
- **Redis 7** - Cache y sesiones
- **drf-spectacular** - Documentación OpenAPI/Swagger

### Frontend
- **React 18** - UI Library
- **Vite** - Build tool y dev server
- **React Router v6** - Routing
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first CSS
- **React Hook Form** - Formularios
- **react-hot-toast** - Notificaciones

### DevOps
- **Docker & Docker Compose** - Containerización
- **Nginx** - Reverse proxy (producción)
- **GitHub Actions** - CI/CD
- **Make** - Automatización de comandos

---

## 🚀 Inicio Rápido

### Prerrequisitos

- Docker y Docker Compose instalados
- Git
- Puertos disponibles: 5173 (frontend), 8000 (backend), 5432 (postgres), 6379 (redis)

### Instalación

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/minimum-api.git
cd minimum-api

# 2. Crear archivos .env desde ejemplos
cp services/backend/.env.example services/backend/.env
cp services/frontend/.env.example services/frontend/.env

# 3. Instalación completa (usando Makefile)
make install

# O manualmente:
docker-compose build
docker-compose up -d
docker exec minimum_api_backend python manage.py migrate
docker exec minimum_api_backend python manage.py seed_roles
docker exec minimum_api_backend python manage.py createsuperuser_auto
```

### Acceso

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/
- **Swagger UI**: http://localhost:8000/api/docs/
- **Django Admin**: http://localhost:8000/admin/

**Credenciales por defecto**:
- Usuario: `admin`
- Password: `admin`

⚠️ **Cambiar en producción**

---

## 📸 Screenshots

### Login
![Login Page](docs/screenshots/01-login.png)
*Página de inicio de sesión con validaciones*

### Dashboard
![Dashboard](docs/screenshots/02-dashboard.png)
*Dashboard principal mostrando información del usuario, roles y permisos*

### Gestión de Usuarios
![Users List](docs/screenshots/03-users-list.png)
*Lista de usuarios con búsqueda, filtros y paginación*

![User Create](docs/screenshots/04-user-create.png)
*Modal de creación de usuario con validaciones*

### API Documentation (Swagger)
![Swagger UI](docs/screenshots/06-swagger.png)
*Documentación interactiva de la API*

### Docker Containers
![Docker](docs/screenshots/07-docker-compose.png)
*Servicios corriendo en Docker*

---

## 📚 Documentación

- [**Getting Started**](docs/GETTING_STARTED.md) - Guía de inicio rápido
- [**Architecture**](docs/ARCHITECTURE.md) - Decisiones de arquitectura y patrones
- [**API Documentation**](docs/API_DOCUMENTATION.md) - Endpoints y ejemplos de uso
- [**Development**](docs/DEVELOPMENT.md) - Guía para desarrolladores
- [**Testing**](docs/TESTING.md) - Cómo ejecutar y escribir tests
- [**Deployment**](docs/DEPLOYMENT.md) - Guía de despliegue (teórica)
- [**Lessons Learned**](docs/LESSONS_LEARNED.md) - Aprendizajes del proyecto

### READMEs Específicos
- [Backend README](services/backend/README.md)
- [Frontend README](services/frontend/README.md)

---

## 🧪 Testing

```bash
# Tests del backend
make test

# Con coverage
make test-coverage

# Tests del frontend
make test-frontend

# Linting
make lint
```

Ver [Testing Guide](docs/TESTING.md) para más detalles.

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Ver [CONTRIBUTING.md](CONTRIBUTING.md) para guías de contribución.

### Flujo de contribución

1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

---

## 📋 Comandos Útiles

```bash
# Ver todos los comandos disponibles
make help

# Levantar servicios
make up

# Ver logs
make logs

# Ejecutar migraciones
make migrate

# Crear backup
make backup

# Abrir shell de Django
make shell-backend

# Abrir shell de PostgreSQL
make shell-db
```

Ver [Makefile](Makefile) para lista completa de comandos.

---

## 🗺️ Roadmap

- [x] Backend con Django REST Framework
- [x] Frontend con React + Vite
- [x] Autenticación JWT completa
- [x] Sistema de permisos
- [x] Cache con Redis
- [x] Docker Compose
- [x] Documentación completa
- [ ] Tests unitarios y E2E completos (parcial)
- [ ] Monitoreo con Prometheus
- [ ] Internacionalización (i18n)
- [ ] WebSockets para notificaciones real-time

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver [LICENSE](LICENSE) para detalles.

---

## 👤 Autor

**Tu Nombre**

- GitHub: [@tu-usuario](https://github.com/tu-usuario)
- LinkedIn: [Tu Perfil](https://linkedin.com/in/tu-perfil)

---

## 🙏 Agradecimientos

- Comunidad de Django y React
- Documentación de DRF
- Tutoriales y recursos de arquitectura limpia
- Todos los contribuidores

---

## 📞 Soporte

Si tienes preguntas o problemas:

1. Revisar la [documentación](docs/)
2. Buscar en [Issues](https://github.com/tu-usuario/minimum-api/issues)
3. Crear un nuevo Issue con detalles

---

**⭐ Si te resultó útil este proyecto, considera darle una estrella en GitHub!**
