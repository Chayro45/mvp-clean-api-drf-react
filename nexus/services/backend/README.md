# Backend - Django REST Framework

Backend del proyecto Minimum API construido con Django 4.2 y Django REST Framework.

---

## 📋 Tecnologías

- **Python 3.12**
- **Django 4.2** - Framework web
- **Django REST Framework 3.15** - API REST
- **SimpleJWT** - Autenticación JWT
- **PostgreSQL 14** - Base de datos
- **Redis 7** - Cache
- **drf-spectacular** - OpenAPI/Swagger

---

## 🏗️ Estructura

```
services/backend/
├── apps/
│   ├── core/              # Funcionalidad compartida
│   ├── users/             # Gestión de usuarios
│   └── auth/              # Autenticación JWT
├── config/
│   ├── settings/
│   │   ├── base.py       # Config compartida
│   │   ├── dev.py        # Desarrollo
│   │   └── prod.py       # Producción
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
└── Dockerfile
```

---

## 🚀 Inicio Rápido

### Con Docker (Recomendado)

```bash
# Desde la raíz del proyecto
docker-compose up -d

# Migraciones
docker exec minimum_api_backend python manage.py migrate

# Crear superusuario
docker exec minimum_api_backend python manage.py createsuperuser_auto
```

### Local (Sin Docker)

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
# Editar DATABASE_URL, REDIS_URL, etc.

# Migraciones
python manage.py migrate

# Crear datos iniciales
python manage.py seed_roles
python manage.py createsuperuser_auto

# Ejecutar servidor
python manage.py runserver
```

---

## 📁 Apps del Backend

### core/

Funcionalidad compartida entre todas las apps.

**Contenido:**
- `BaseModel`, `TimestampedModel`, `SoftDeleteModel` - Modelos base
- `permissions.py` - Helpers de permisos y cache
- `HealthCheckView` - Endpoint de health check
- Management commands: `wait_for_db`

**Ver:** [core/README.md](apps/core/README.md)

---

### users/

Gestión de usuarios y perfiles.

**Modelos:**
- `UserProfile` (OneToOne con User nativo)

**Endpoints:**
- `GET /api/users/` - Listar usuarios
- `POST /api/users/` - Crear usuario
- `GET /api/users/{id}/` - Obtener usuario
- `PUT /api/users/{id}/` - Actualizar usuario
- `DELETE /api/users/{id}/` - Inactivar usuario (soft delete)
- `POST /api/users/{id}/change_password/` - Cambiar password
- `GET /api/users/groups/` - Listar grupos (roles)

**Ver:** [users/README.md](apps/users/README.md)

---

### auth/

Autenticación JWT.

**Endpoints:**
- `POST /api/auth/login/` - Login (obtener tokens)
- `POST /api/auth/refresh/` - Refresh access token
- `POST /api/auth/logout/` - Logout (blacklist refresh)
- `POST /api/auth/verify/` - Verificar token
- `GET /api/auth/me/` - Usuario actual

**Ver:** [auth/README.md](apps/auth/README.md)

---

## 🔑 Variables de Entorno

Ver `.env.example` para lista completa. Las principales:

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Redis
REDIS_URL=redis://host:port/db

# JWT
JWT_ACCESS_TOKEN_MINUTES=30
JWT_REFRESH_TOKEN_DAYS=7

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

---

## 🧪 Tests

```bash
# Todos los tests
python manage.py test

# App específica
python manage.py test apps.users

# Con coverage
coverage run --source='apps' manage.py test
coverage report
```

---

## 🛠️ Management Commands

```bash
# Esperar por la base de datos (útil en Docker)
python manage.py wait_for_db

# Crear roles y permisos iniciales
python manage.py seed_roles

# Crear superusuario automático (desarrollo)
python manage.py createsuperuser_auto
```

---

## 📚 API Documentation

**Swagger UI**: http://localhost:8000/api/docs/

Documentación interactiva generada automáticamente con drf-spectacular.

---

## 🏛️ Arquitectura

### Capas

```
┌─────────────────────────────────────┐
│  API Layer (views, serializers)    │
├─────────────────────────────────────┤
│  Application Layer (services)      │
├─────────────────────────────────────┤
│  Domain Layer (models)             │
├─────────────────────────────────────┤
│  Infrastructure (cache, external)  │
└─────────────────────────────────────┘
```

### Ejemplo: users app

```
apps/users/
├── api/
│   ├── views.py         # UserViewSet
│   ├── serializers.py   # UserSerializer, UserCreateSerializer
│   └── urls.py          # Routing
├── application/
│   └── services.py      # UserService (lógica de negocio)
├── domain/
│   └── models.py        # UserProfile
└── infrastructure/
    └── cache.py         # UserPermissionCache
```

---

## 🔐 Autenticación

### JWT Flow

```
1. Login → Recibir access + refresh tokens
2. Incluir access token en header: Authorization: Bearer <token>
3. Si access expira → Usar refresh token para obtener nuevo access
4. Logout → Blacklist del refresh token
```

### Permisos

Sistema nativo de Django:
- User → Groups (roles) → Permissions
- Cache en Redis (TTL 1 hora)
- Invalidación manual al cambiar grupos

---

## 🚀 Deployment

Ver [DEPLOYMENT.md](../../docs/DEPLOYMENT.md) para guía completa.

**Producción:**
- DEBUG=False
- ALLOWED_HOSTS configurado
- SECRET_KEY único y seguro
- HTTPS/SSL
- Gunicorn como WSGI server
- Nginx como reverse proxy

---

## 📝 Convenciones de Código

### Python Style Guide

```bash
# Formatear con black
black apps/

# Linting con flake8
flake8 apps/

# Ordenar imports con isort
isort apps/
```

### Naming

- Variables/funciones: `snake_case`
- Clases: `PascalCase`
- Constantes: `UPPER_SNAKE_CASE`

### Docstrings

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
    """
    pass
```

---

## 📦 Dependencias Principales

```
Django==4.2.10
djangorestframework==3.15.1
djangorestframework-simplejwt==5.3.1
drf-spectacular==0.27.2
psycopg2-binary==2.9.9
redis==5.0.1
django-cors-headers==4.3.1
django-filter==24.1
gunicorn==21.2.0
```

Ver `requirements.txt` para lista completa.

---

## 🐛 Troubleshooting

### Error: "relation does not exist"

```bash
# Ejecutar migraciones
python manage.py migrate
```

### Error: "FATAL: password authentication failed"

Verificar DATABASE_URL en `.env`.

### Error: "Connection refused" (Redis)

```bash
# Verificar que Redis esté corriendo
redis-cli ping
# Debería retornar: PONG
```

---

## 📖 Recursos

- [Django Documentation](https://docs.djangoproject.com/)
- [DRF Documentation](https://www.django-rest-framework.org/)
- [SimpleJWT Documentation](https://django-rest-framework-simplejwt.readthedocs.io/)

---

**Ver también:**
- [Architecture Guide](../../docs/ARCHITECTURE.md)
- [API Documentation](../../docs/API_DOCUMENTATION.md)
- [Development Guide](../../docs/DEVELOPMENT.md)
