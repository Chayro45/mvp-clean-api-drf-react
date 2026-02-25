# 📡 API Documentation

Documentación completa de los endpoints de la API REST.

**Base URL**: `http://localhost:8000/api`

**Autenticación**: JWT Bearer Token

---

## Tabla de Contenidos

- [Autenticación](#autenticación)
- [Usuarios](#usuarios)
- [Grupos (Roles)](#grupos-roles)
- [Health Check](#health-check)
- [Códigos de Estado](#códigos-de-estado)
- [Manejo de Errores](#manejo-de-errores)

---

## Autenticación

### Login

Obtiene tokens JWT (access + refresh) para autenticación.

**Endpoint**: `POST /auth/login/`

**Request**:
```json
{
  "username": "admin",
  "password": "admin"
}
```

**Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "roles": ["Administradores"],
    "permissions": ["auth.add_user", "auth.change_user", ...],
    "is_active": true,
    "is_superuser": true
  }
}
```

**Errores**:
- `400 Bad Request`: Credenciales inválidas
- `429 Too Many Requests`: Rate limit excedido (5 intentos/min)

**Ejemplo cURL**:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

---

### Refresh Token

Renueva el access token usando el refresh token.

**Endpoint**: `POST /auth/refresh/`

**Request**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Nota**: Si `ROTATE_REFRESH_TOKENS=True`, también retorna nuevo refresh token.

---

### Logout

Invalida el refresh token (lo agrega a blacklist).

**Endpoint**: `POST /auth/logout/`

**Headers**:
```
Authorization: Bearer <access-token>
```

**Request**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response** (200 OK):
```json
{
  "detail": "Logout exitoso"
}
```

---

### Verify Token

Verifica si un token es válido.

**Endpoint**: `POST /auth/verify/`

**Request**:
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response** (200 OK):
```json
{}
```

**Errores**:
- `401 Unauthorized`: Token inválido o expirado

---

### Current User

Obtiene información del usuario autenticado.

**Endpoint**: `GET /auth/me/`

**Headers**:
```
Authorization: Bearer <access-token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "full_name": "Admin User",
  "first_name": "Admin",
  "last_name": "User",
  "roles": ["Administradores"],
  "permissions": ["auth.add_user", ...],
  "profile": {
    "phone": "+1234567890",
    "department": "IT",
    "employee_id": "EMP001",
    "avatar_url": null
  },
  "is_active": true,
  "is_superuser": true,
  "is_staff": true,
  "date_joined": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-15T10:30:00Z"
}
```

---

## Usuarios

### Listar Usuarios

Lista todos los usuarios con paginación.

**Endpoint**: `GET /users/`

**Headers**:
```
Authorization: Bearer <access-token>
```

**Query Parameters**:
- `page` (int): Número de página (default: 1)
- `search` (string): Buscar por username, email, nombre
- `is_active` (bool): Filtrar por estado
- `ordering` (string): Ordenar por campo (ej: `-date_joined`)

**Ejemplo**:
```
GET /users/?page=1&search=admin&is_active=true
```

**Response** (200 OK):
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "full_name": "Admin User",
      "first_name": "Admin",
      "last_name": "User",
      "roles": ["Administradores"],
      "groups": [
        {
          "id": 1,
          "name": "Administradores"
        }
      ],
      "profile": {
        "phone": "+1234567890",
        "department": "IT"
      },
      "is_active": true,
      "date_joined": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**Permisos requeridos**: `auth.view_user`

---

### Obtener Usuario

Obtiene detalles de un usuario específico.

**Endpoint**: `GET /users/{id}/`

**Headers**:
```
Authorization: Bearer <access-token>
```

**Response** (200 OK): Mismo formato que item en lista

**Errores**:
- `404 Not Found`: Usuario no existe

**Permisos requeridos**: `auth.view_user`

---

### Crear Usuario

Crea un nuevo usuario.

**Endpoint**: `POST /users/`

**Headers**:
```
Authorization: Bearer <access-token>
Content-Type: application/json
```

**Request**:
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "first_name": "New",
  "last_name": "User",
  "phone": "+1234567890",
  "department": "Sales",
  "employee_id": "EMP002",
  "group_ids": [2],
  "is_active": true
}
```

**Campos requeridos**:
- `username` (string, 3-150 chars, alfanumérico + _)
- `email` (string, formato email válido)
- `password` (string, min 8 chars)
- `password_confirm` (string, debe coincidir con password)

**Campos opcionales**:
- `first_name`, `last_name` (string)
- `phone` (string)
- `department` (string)
- `employee_id` (string)
- `group_ids` (array de integers, IDs de grupos)
- `is_active` (boolean, default: true)

**Response** (201 Created):
```json
{
  "id": 2,
  "username": "newuser",
  "email": "newuser@example.com",
  "full_name": "New User",
  ...
}
```

**Errores**:
- `400 Bad Request`: Validación fallida
- `403 Forbidden`: Sin permisos

**Permisos requeridos**: `auth.add_user`

---

### Actualizar Usuario

Actualiza un usuario existente (reemplaza todos los campos).

**Endpoint**: `PUT /users/{id}/`

**Headers**:
```
Authorization: Bearer <access-token>
Content-Type: application/json
```

**Request**:
```json
{
  "email": "updated@example.com",
  "first_name": "Updated",
  "last_name": "Name",
  "phone": "+9876543210",
  "department": "Engineering",
  "employee_id": "EMP002",
  "group_ids": [1, 2],
  "is_active": true
}
```

**Nota**: `username` NO se puede cambiar. `password` se cambia con endpoint separado.

**Response** (200 OK): Usuario actualizado

**Permisos requeridos**: `auth.change_user`

**Validaciones de negocio**:
- No puede desactivarse a sí mismo
- No puede remover su propio rol de Administrador

---

### Actualización Parcial

Actualiza solo campos específicos.

**Endpoint**: `PATCH /users/{id}/`

**Request** (ejemplo):
```json
{
  "department": "Marketing"
}
```

**Response** (200 OK): Usuario actualizado

---

### Eliminar Usuario (Inactivar)

Soft delete: marca como inactivo en lugar de borrar.

**Endpoint**: `DELETE /users/{id}/`

**Headers**:
```
Authorization: Bearer <access-token>
```

**Response** (204 No Content)

**Permisos requeridos**: `auth.delete_user`

**Validaciones**:
- No puede eliminarse a sí mismo

**Nota**: Los datos permanecen en DB con `is_active=False`.

---

### Usuario Actual (Shortcut)

Atajo para obtener usuario autenticado.

**Endpoint**: `GET /users/me/`

**Headers**:
```
Authorization: Bearer <access-token>
```

**Response** (200 OK): Mismo que `/auth/me/`

---

### Cambiar Password

Cambia la contraseña de un usuario.

**Endpoint**: `POST /users/{id}/change_password/`

**Headers**:
```
Authorization: Bearer <access-token>
Content-Type: application/json
```

**Request**:
```json
{
  "old_password": "currentpass123",
  "new_password": "newsecurepass456",
  "new_password_confirm": "newsecurepass456"
}
```

**Response** (200 OK):
```json
{
  "detail": "Contraseña actualizada exitosamente"
}
```

**Errores**:
- `400 Bad Request`: Password actual incorrecta o passwords no coinciden

**Validaciones**:
- Usuario normal debe proporcionar `old_password`
- Superuser puede cambiar sin `old_password` (de otros usuarios)

---

## Grupos (Roles)

### Listar Grupos

Lista todos los grupos (roles) disponibles.

**Endpoint**: `GET /users/groups/`

**Headers**:
```
Authorization: Bearer <access-token>
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "name": "Administradores"
  },
  {
    "id": 2,
    "name": "Operadores"
  },
  {
    "id": 3,
    "name": "Usuarios"
  }
]
```

---

## Health Check

### Verificar Estado del Sistema

Verifica que todos los servicios estén funcionando.

**Endpoint**: `GET /health/`

**No requiere autenticación**

**Response** (200 OK - Healthy):
```json
{
  "status": "healthy",
  "database": "connected",
  "cache": "connected"
}
```

**Response** (503 Service Unavailable - Unhealthy):
```json
{
  "status": "unhealthy",
  "database": "error: connection refused",
  "cache": "connected"
}
```

**Uso**: Ideal para health checks de Docker, Kubernetes, load balancers.

---

## Códigos de Estado

| Código | Significado | Cuándo se usa |
|--------|-------------|---------------|
| 200 | OK | Request exitoso (GET, PUT, PATCH) |
| 201 | Created | Recurso creado exitosamente (POST) |
| 204 | No Content | Recurso eliminado exitosamente (DELETE) |
| 400 | Bad Request | Validación fallida, datos inválidos |
| 401 | Unauthorized | Token inválido, expirado o ausente |
| 403 | Forbidden | Token válido pero sin permisos |
| 404 | Not Found | Recurso no existe |
| 429 | Too Many Requests | Rate limit excedido |
| 500 | Internal Server Error | Error del servidor |
| 503 | Service Unavailable | Servicio temporalmente no disponible |

---

## Manejo de Errores

### Formato de Error Estándar

```json
{
  "detail": "Mensaje de error descriptivo"
}
```

### Errores de Validación

```json
{
  "username": ["Este campo es requerido"],
  "email": ["Ingresa un email válido"],
  "password": ["La contraseña debe tener al menos 8 caracteres"]
}
```

### Ejemplos de Errores Comunes

#### 401 Unauthorized

```json
{
  "detail": "No se proporcionaron credenciales de autenticación."
}
```

**Solución**: Incluir header `Authorization: Bearer <token>`

---

#### 403 Forbidden

```json
{
  "detail": "No tienes permisos para realizar esta acción."
}
```

**Solución**: Usuario necesita el permiso correspondiente

---

#### 429 Too Many Requests

```json
{
  "detail": "Request was throttled. Expected available in 45 seconds."
}
```

**Solución**: Esperar el tiempo indicado antes de reintentar

---

## Rate Limiting

| Endpoint | Límite |
|----------|--------|
| `/auth/login/` | 5 requests/minuto |
| Otros endpoints (autenticado) | 1000 requests/hora |
| Otros endpoints (anónimo) | 100 requests/hora |

---

## Paginación

Todos los endpoints de lista usan paginación.

**Parámetros**:
- `page`: Número de página (default: 1)
- `page_size`: Items por página (max: 100, default: 20)

**Response**:
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/users/?page=3",
  "previous": "http://localhost:8000/api/users/?page=1",
  "results": [...]
}
```

---

## Filtrado y Búsqueda

### Búsqueda (search)

Busca en múltiples campos:

```
GET /users/?search=admin
```

Busca en: `username`, `email`, `first_name`, `last_name`

### Filtros específicos

```
GET /users/?is_active=true
GET /users/?is_staff=true
```

### Ordenamiento

```
GET /users/?ordering=-date_joined    # Más recientes primero
GET /users/?ordering=username        # A-Z
GET /users/?ordering=-username       # Z-A
```

---

## Swagger UI

Para explorar la API interactivamente:

**URL**: http://localhost:8000/api/docs/

**Características**:
- Documentación automática
- Probar endpoints directamente
- Ver schemas de request/response
- Autenticación JWT integrada

**Cómo autenticar en Swagger**:
1. Hacer login en `/api/auth/login/`
2. Copiar el `access` token
3. Click en "Authorize" (candado arriba)
4. Ingresar: `Bearer <access-token>`
5. Click "Authorize"
6. ¡Ya puedes probar endpoints protegidos!

---

## Postman Collection

Importar: `docs/postman/Minimum_API_Collection.json`

**Incluye**:
- Todos los endpoints documentados
- Variables de entorno
- Tests automáticos
- Auto-guardado de tokens

---

## Próximos Pasos

- [Development Guide](DEVELOPMENT.md) - Extender la API
- [Testing Guide](TESTING.md) - Probar endpoints
- [Architecture](ARCHITECTURE.md) - Entender el diseño
