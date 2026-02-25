/**
 * pages/DashboardPage.jsx
 * 
 * Dashboard principal - Vista después de login
 */

import { useAuth } from '@context/AuthContext';
import Navbar from '@components/common/Navbar';

const DashboardPage = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="px-4 py-6 sm:px-0">
          <h1 className="text-3xl font-bold text-gray-900">
            ¡Bienvenido, {user?.first_name || user?.username}!
          </h1>
          <p className="mt-2 text-gray-600">
            Este es tu panel de control
          </p>
        </div>

        {/* Cards de información */}
        <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {/* Card de perfil */}
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Tu Perfil
            </h3>
            <dl className="space-y-2">
              <div>
                <dt className="text-sm font-medium text-gray-500">Usuario</dt>
                <dd className="text-sm text-gray-900">{user?.username}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Email</dt>
                <dd className="text-sm text-gray-900">{user?.email}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Nombre completo</dt>
                <dd className="text-sm text-gray-900">{user?.full_name}</dd>
              </div>
            </dl>
          </div>

          {/* Card de roles */}
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Roles
            </h3>
            <div className="space-y-2">
              {user?.roles && user.roles.length > 0 ? (
                user.roles.map((role, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800"
                  >
                    {role}
                  </span>
                ))
              ) : (
                <p className="text-sm text-gray-500">Sin roles asignados</p>
              )}
            </div>
          </div>

          {/* Card de permisos */}
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Permisos
            </h3>
            <div className="max-h-40 overflow-y-auto">
              {user?.permissions && user.permissions.length > 0 ? (
                <ul className="space-y-1">
                  {user.permissions.slice(0, 5).map((permission, index) => (
                    <li key={index} className="text-sm text-gray-600">
                      • {permission}
                    </li>
                  ))}
                  {user.permissions.length > 5 && (
                    <li className="text-sm text-gray-500 italic">
                      + {user.permissions.length - 5} más
                    </li>
                  )}
                </ul>
              ) : (
                <p className="text-sm text-gray-500">Sin permisos específicos</p>
              )}
            </div>
          </div>
        </div>

        {/* Stats adicionales */}
        <div className="mt-8">
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Información de Cuenta
            </h3>
            <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <dt className="text-sm font-medium text-gray-500">Estado</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    user?.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {user?.is_active ? 'Activo' : 'Inactivo'}
                  </span>
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Tipo de usuario</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {user?.is_superuser ? 'Superusuario' : user?.is_staff ? 'Staff' : 'Usuario'}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Fecha de registro</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {user?.date_joined ? new Date(user.date_joined).toLocaleDateString() : 'N/A'}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Último acceso</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {user?.last_login ? new Date(user.last_login).toLocaleString() : 'Primer acceso'}
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
