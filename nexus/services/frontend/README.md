# Frontend - React + Vite

Frontend del proyecto Minimum API construido con React 18 y Vite.

---

## 📋 Tecnologías

- **React 18** - UI Library
- **Vite** - Build tool y dev server
- **React Router v6** - Routing
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first CSS
- **React Hook Form** - Formularios y validaciones
- **react-hot-toast** - Notificaciones

---

## 🏗️ Estructura

```
services/frontend/
├── src/
│   ├── components/
│   │   ├── auth/          # Componentes de autenticación
│   │   ├── common/        # Componentes reutilizables
│   │   └── users/         # Componentes de usuarios
│   ├── context/
│   │   └── AuthContext.jsx  # State global de auth
│   ├── hooks/
│   │   └── useIdleTimeout.js  # Custom hooks
│   ├── pages/
│   │   ├── LoginPage.jsx
│   │   ├── DashboardPage.jsx
│   │   └── UsersPage.jsx
│   ├── services/
│   │   ├── api.js           # Axios instance
│   │   ├── authService.js   # Auth API calls
│   │   └── userService.js   # Users API calls
│   ├── utils/
│   │   └── errorMessages.js # Helper de errores
│   ├── App.jsx              # Routing principal
│   ├── main.jsx             # Entry point
│   └── index.css            # Estilos globales
├── public/
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

---

## 🚀 Inicio Rápido

### Con Docker (Recomendado)

```bash
# Desde la raíz del proyecto
docker-compose up -d

# Acceder a
# http://localhost:5173
```

### Local (Sin Docker)

```bash
cd services/frontend

# Instalar dependencias
npm install

# Configurar .env
cp .env.example .env
# Editar VITE_API_URL

# Ejecutar dev server
npm run dev

# Build para producción
npm run build

# Preview del build
npm run preview
```

---

## 🔑 Variables de Entorno

```bash
# .env
VITE_API_URL=http://localhost:8000/api
VITE_ENV=development
```

**Nota**: Variables deben empezar con `VITE_` para ser expuestas.

---

## 📁 Componentes Principales

### Context API

**AuthContext**: State global de autenticación

```javascript
const { user, login, logout, isAuthenticated } = useAuth();
```

**Funcionalidad:**
- Login/Logout
- Auto-refresh de JWT
- Detección de inactividad
- Sync entre tabs

---

### Protected Routes

```javascript
<Route path="/dashboard" element={
  <ProtectedRoute>
    <DashboardPage />
  </ProtectedRoute>
} />

// Con permisos
<Route path="/users" element={
  <ProtectedRoute permission="auth.view_user">
    <UsersPage />
  </ProtectedRoute>
} />
```

---

### Services Layer

Encapsula todas las llamadas al API:

```javascript
// authService.js
await authService.login(username, password);
await authService.logout();
await authService.getCurrentUser();

// userService.js
await userService.getUsers({ page: 1, search: 'john' });
await userService.createUser(userData);
await userService.updateUser(id, userData);
await userService.deleteUser(id);
```

---

### Axios Interceptors

Auto-refresh transparente de JWT:

```javascript
// services/api.js
api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      // Auto-refresh token
      const newToken = await refreshToken();
      // Retry request con nuevo token
      return api(originalRequest);
    }
  }
);
```

---

## 🎨 Tailwind CSS

### Utility Classes

```jsx
<div className="flex items-center justify-between p-4 bg-white rounded-lg shadow-md">
  <h1 className="text-2xl font-bold text-gray-900">Título</h1>
</div>
```

### Custom Classes (index.css)

```css
.btn { @apply px-4 py-2 rounded-lg font-medium; }
.btn-primary { @apply bg-primary-600 text-white hover:bg-primary-700; }
.input { @apply w-full px-3 py-2 border rounded-lg; }
.card { @apply bg-white rounded-lg shadow-md p-6; }
```

---

## 📋 Páginas

### LoginPage

- Formulario de login
- Validaciones
- Redirect automático si ya está autenticado

### DashboardPage

- Información del usuario
- Roles y permisos
- Estadísticas de cuenta

### UsersPage

- Lista de usuarios con paginación
- Búsqueda y filtros
- CRUD completo (crear, editar, eliminar)
- Modals para formularios

---

## 🔐 Autenticación

### Flow

```
1. Usuario ingresa credenciales
2. AuthContext.login() llama authService.login()
3. Tokens guardados en localStorage
4. Usuario redirigido a dashboard
5. Requests incluyen access token en header
6. Si token expira, auto-refresh transparente
7. Si refresh también expira, logout + redirect a login
```

### Inactividad

- Detecta 10 minutos de inactividad
- Muestra modal con countdown (60 seg)
- Usuario puede continuar o hacer logout
- Si no responde, logout automático

### Sync Entre Tabs

```javascript
// Si otra tab hace logout
window.addEventListener('storage', (e) => {
  if (e.key === 'access_token' && !e.newValue) {
    logout();
    navigate('/login');
  }
});
```

---

## 🧪 Tests

```bash
# Ejecutar tests
npm test

# Con coverage
npm run test:coverage

# Watch mode
npm test -- --watch
```

---

## 🏗️ Build

```bash
# Build de producción
npm run build

# Output: dist/

# Preview
npm run preview
```

---

## 📦 Dependencias Principales

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.22.0",
  "axios": "^1.6.7",
  "react-hook-form": "^7.50.1",
  "react-hot-toast": "^2.4.1"
}
```

**DevDependencies:**
```json
{
  "vite": "^5.1.0",
  "tailwindcss": "^3.4.1",
  "@vitejs/plugin-react": "^4.2.1"
}
```

---

## 🎯 Patrones Implementados

### 1. Container/Presenter

```jsx
// Container (lógica)
const UsersPage = () => {
  const [users, loading] = useUsers();
  return <UsersList users={users} loading={loading} />;
};

// Presenter (UI)
const UsersList = ({ users, loading }) => {
  if (loading) return <LoadingSpinner />;
  return <div>{/* render users */}</div>;
};
```

### 2. Custom Hooks

```javascript
const useUsers = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadUsers();
  }, []);
  
  return { users, loading, refetch: loadUsers };
};
```

### 3. Error Boundaries (próximamente)

```jsx
<ErrorBoundary fallback={<ErrorPage />}>
  <App />
</ErrorBoundary>
```

---

## 🎨 Componentes Reutilizables

### Modal

```jsx
<Modal 
  isOpen={showModal} 
  onClose={() => setShowModal(false)}
  title="Crear Usuario"
>
  <UserForm />
</Modal>
```

### LoadingSpinner

```jsx
<LoadingSpinner size="lg" text="Cargando..." />
```

### ConfirmDialog (próximamente)

```jsx
<ConfirmDialog
  isOpen={showConfirm}
  onConfirm={handleDelete}
  title="¿Eliminar usuario?"
  message="Esta acción no se puede deshacer"
/>
```

---

## 🚀 Performance

### Code Splitting

```jsx
// Lazy loading de páginas
const UsersPage = lazy(() => import('./pages/UsersPage'));

<Suspense fallback={<LoadingSpinner />}>
  <UsersPage />
</Suspense>
```

### Memoization

```jsx
const UserCard = memo(({ user }) => {
  // Solo re-renderiza si user cambia
});
```

---

## 🐛 Troubleshooting

### Error: "Cannot find module '@/...'"

Verificar alias en `vite.config.js`:

```javascript
resolve: {
  alias: {
    '@': path.resolve(__dirname, './src'),
    '@components': path.resolve(__dirname, './src/components'),
  },
}
```

### Error: "CORS error"

Verificar que backend tenga configurado:
```python
CORS_ALLOWED_ORIGINS = ['http://localhost:5173']
```

### Token refresh loop

Limpiar localStorage:
```javascript
localStorage.clear();
```

---

## 📝 Convenciones de Código

### Naming

- Componentes: `PascalCase` (UserCard.jsx)
- Archivos JS: `camelCase` (authService.js)
- Variables/funciones: `camelCase`
- Constantes: `UPPER_SNAKE_CASE`

### Estructura de Componente

```jsx
/**
 * UserCard - Muestra información de usuario
 * 
 * @param {Object} props
 * @param {Object} props.user - Datos del usuario
 * @param {Function} props.onEdit - Callback al editar
 */
const UserCard = ({ user, onEdit }) => {
  // Hooks
  const [expanded, setExpanded] = useState(false);
  
  // Handlers
  const handleClick = () => {
    setExpanded(!expanded);
  };
  
  // Render
  return (
    <div onClick={handleClick}>
      {/* JSX */}
    </div>
  );
};

export default UserCard;
```

---

## 🔧 Configuración Adicional

### ESLint

```bash
npm install -D eslint eslint-plugin-react
npm run lint
```

### Prettier

```bash
npm install -D prettier
npm run format
```

---

## 📖 Recursos

- [React Docs](https://react.dev/)
- [Vite Docs](https://vitejs.dev/)
- [React Router](https://reactrouter.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [React Hook Form](https://react-hook-form.com/)

---

**Ver también:**
- [Architecture Guide](../../docs/ARCHITECTURE.md)
- [Development Guide](../../docs/DEVELOPMENT.md)
- [API Documentation](../../docs/API_DOCUMENTATION.md)
