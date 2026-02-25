/**
 * components/common/Navbar.jsx
 * 
 * Barra de navegación principal
 */

import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@context/AuthContext';

const Navbar = () => {
  const navigate = useNavigate();
  const { user, logout, hasPermission } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo y links */}
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link to="/dashboard" className="text-xl font-bold text-primary-600">
                Minimum API
              </Link>
            </div>

            {/* Navigation links */}
            <div className="hidden sm:ml-8 sm:flex sm:space-x-8">
              <Link
                to="/dashboard"
                className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 hover:text-primary-600 transition-colors"
              >
                Dashboard
              </Link>

              {/* Mostrar link de usuarios solo si tiene permiso */}
              {hasPermission('auth.view_user') && (
                <Link
                  to="/users"
                  className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 hover:text-primary-600 transition-colors"
                >
                  Usuarios
                </Link>
              )}
            </div>
          </div>

          {/* User menu */}
          <div className="flex items-center">
            <div className="flex items-center space-x-4">
              {/* User info */}
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  {user?.full_name || user?.username}
                </p>
                <p className="text-xs text-gray-500">
                  {user?.roles?.join(', ') || 'Usuario'}
                </p>
              </div>

              {/* Logout button */}
              <button
                onClick={handleLogout}
                className="btn btn-secondary text-sm"
              >
                Salir
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile menu (opcional - implementar si se necesita) */}
    </nav>
  );
};

export default Navbar;