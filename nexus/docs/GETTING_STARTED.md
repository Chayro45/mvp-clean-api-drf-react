# 🚀 Getting Started - Guía de Inicio Rápido

Esta guía te ayudará a tener el proyecto corriendo en menos de 10 minutos.

---

## Prerrequisitos

Antes de empezar, asegúrate de tener instalado:

- **Docker** (versión 20.10+)
- **Docker Compose** (versión 2.0+)
- **Git**
- **Make** (opcional, facilita comandos)

### Verificar instalación

```bash
docker --version
# Docker version 20.10.x

docker-compose --version
# Docker Compose version v2.x.x

git --version
# git version 2.x.x

make --version  # Opcional
# GNU Make 4.x
```

---

## Instalación Rápida

### Opción A: Con Makefile (Recomendado)

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/minimum-api.git
cd minimum-api

# 2. Copiar archivos de entorno
cp services/backend/.env.example services/backend/.env
cp services/frontend/.env.example services/frontend/.env

# 3. Instalación automática (build + migrate + seed + superuser)
make install

# ¡Listo! 🎉
```

### Opción B: Manual (sin Make)

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/minimum-api.git
cd minimum-api

# 2. Copiar archivos de entorno
cp services/backend/.env.example services/backend/.env
cp services/frontend/.env.example services/frontend/.env

# 3. Construir imágenes
docker-compose build

# 4. Levantar servicios
docker-compose up -d

# 5. Ejecutar migraciones
docker exec minimum_api_backend python manage.py migrate

# 6. Crear roles y permisos
docker exec minimum_api_backend python manage.py seed_roles

# 7. Crear superusuario
docker exec minimum_api_backend python manage.py createsuperuser_auto

# ¡Listo! 🎉
```

---

## Verificar Instalación

### 1. Ver contenedores corriendo

```bash
docker-compose ps

# Deberías ver 4 contenedores:
# - minimum_api_backend
# - minimum_api_frontend
# - minimum_api_db
# - minimum_api_redis
```

### 2. Verificar logs

```bash
# Ver logs de todos los servicios
docker-compose logs

# O de uno específico
docker-compose logs backend
docker-compose logs frontend
```

### 3. Health Check

```bash
# Backend health
curl http://localhost:8000/health/

# Respuesta esperada:
# {"status":"healthy","database":"connected","cache":"connected"}
```

---

## Acceder a la Aplicación

### Frontend

**URL**: http://localhost:5173

**Credenciales**:
- Usuario: `admin`
- Password: `admin`

**Navegación**:
1. Login → Dashboard
2. Click en "Usuarios" en navbar
3. Crear, editar, eliminar usuarios
4. Probar búsqueda y filtros

---

### Backend API

**Swagger UI**: http://localhost:8000/api/docs/

Documentación interactiva donde puedes:
- Ver todos los endpoints
- Probar requests directamente
- Ver schemas de request/response

**Cómo usar Swagger**:
1. Ir a http://localhost:8000/api/docs/
2. Click en "Authorize" (candado arriba)
3. Login en frontend para obtener token
4. O usar endpoint `/api/auth/login/` en Swagger
5. Copiar `access` token del response
6. En Authorize, poner: `Bearer <tu-access-token>`
7. Probar cualquier endpoint

---

### Django Admin

**URL**: http://localhost:8000/admin/

**Credenciales**: `admin` / `admin`

Aquí puedes:
- Ver modelos directamente
- Crear usuarios manualmente
- Asignar grupos (roles)
- Ver permisos

---

## Estructura del Proyecto

```
minimum-api/
├── services/
│   ├── backend/          # Django + DRF
│   │   ├── apps/
│   │   │   ├── core/     # Funcionalidad compartida
│   │   │   ├── users/    # Gestión de usuarios
│   │   │   └── auth/     # Autenticación JWT
│   │   ├── config/       # Configuración Django
│   │   └── manage.py
│   │
│   └── frontend/         # React + Vite
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   ├── services/
│       │   └── context/
│       └── package.json
│
├── docs/                 # Documentación
├── scripts/              # Scripts útiles (backup, etc.)
├── docker-compose.yml    # Configuración Docker
└── Makefile             # Comandos útiles
```

---

## Comandos Comunes

### Con Makefile

```bash
# Ver todos los comandos disponibles
make help

# Levantar servicios
make up

# Bajar servicios
make down

# Reiniciar servicios
make restart

# Ver logs
make logs

# Ver logs de un servicio específico
make logs-backend
make logs-frontend

# Ejecutar tests
make test

# Limpiar todo (contenedores + volúmenes)
make clean
```

### Comandos Docker Compose

```bash
# Levantar servicios
docker-compose up -d

# Bajar servicios
docker-compose down

# Ver logs
docker-compose logs -f

# Reiniciar un servicio
docker-compose restart backend

# Reconstruir imágenes
docker-compose build

# Ejecutar comando en contenedor
docker exec -it minimum_api_backend bash
```

---

## Gestión de Base de Datos

### Migraciones

```bash
# Crear migraciones
make makemigrations
# O: docker exec minimum_api_backend python manage.py makemigrations

# Ejecutar migraciones
make migrate
# O: docker exec minimum_api_backend python manage.py migrate

# Ver migraciones
docker exec minimum_api_backend python manage.py showmigrations
```

### Acceder a PostgreSQL

```bash
# Con make
make shell-db

# O manualmente
docker exec -it minimum_api_db psql -U postgres -d minimum_api

# Dentro de psql:
\dt              # Listar tablas
\d auth_user     # Ver estructura de tabla
SELECT * FROM auth_user;
\q               # Salir
```

### Backup y Restore

```bash
# Crear backup
make backup
# Genera: backups/backup_minimum_api_YYYYMMDD_HHMMSS.sql.gz

# Restaurar backup
make restore FILE=backups/backup_20240101_120000.sql.gz
```

---

## Desarrollo

### Backend (Django)

```bash
# Abrir shell de Django
make shell-backend
# O: docker exec -it minimum_api_backend bash

# Dentro del shell:
python manage.py shell
```

### Frontend (React)

```bash
# Abrir shell de Node
docker exec -it minimum_api_frontend sh

# Instalar dependencia nueva
docker exec minimum_api_frontend npm install <paquete>

# Reconstruir
docker-compose restart frontend
```

---

## Solución de Problemas

### Puerto ya en uso

```bash
# Error: "port is already allocated"

# Ver qué proceso usa el puerto
lsof -i :8000  # Backend
lsof -i :5173  # Frontend
lsof -i :5432  # PostgreSQL

# Matar proceso
kill -9 <PID>

# O cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Usar 8001 en lugar de 8000
```

### Contenedores no inician

```bash
# Ver logs de error
docker-compose logs backend

# Reconstruir desde cero
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Frontend no se conecta al backend

1. Verificar `.env` en frontend:
   ```bash
   VITE_API_URL=http://localhost:8000/api
   ```

2. Verificar CORS en backend (`config/settings/dev.py`):
   ```python
   CORS_ALLOWED_ORIGINS = [
       'http://localhost:5173',
   ]
   ```

3. Reiniciar servicios:
   ```bash
   docker-compose restart backend frontend
   ```

### Error de migraciones

```bash
# Resetear base de datos (⚠️ PIERDE DATOS)
docker-compose down -v
docker-compose up -d
make migrate
make seed
make superuser
```

---

## Siguientes Pasos

Una vez que todo funciona:

1. **Explorar el código**:
   - Revisar `services/backend/apps/`
   - Revisar `services/frontend/src/`

2. **Leer documentación**:
   - [Architecture](ARCHITECTURE.md) - Entender decisiones de diseño
   - [API Documentation](API_DOCUMENTATION.md) - Endpoints disponibles
   - [Development](DEVELOPMENT.md) - Guía para desarrolladores

3. **Experimentar**:
   - Crear usuarios con diferentes roles
   - Probar permisos
   - Explorar Swagger UI
   - Ver cómo funciona auto-refresh de JWT

4. **Modificar y aprender**:
   - Agregar un campo nuevo a UserProfile
   - Crear un nuevo endpoint
   - Agregar una página nueva en frontend

---

## Recursos Adicionales

- **Django Docs**: https://docs.djangoproject.com/
- **DRF Docs**: https://www.django-rest-framework.org/
- **React Docs**: https://react.dev/
- **Vite Docs**: https://vitejs.dev/

---

**¿Problemas?** Abre un [Issue en GitHub](https://github.com/tu-usuario/minimum-api/issues)

**¿Todo funcionando?** ¡Continúa con [Development Guide](DEVELOPMENT.md)!
