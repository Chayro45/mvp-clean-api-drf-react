/**
 * components/auth/ProtectedRoute.jsx
 * 
 * Componente para proteger rutas que requieren autenticación
 */

import { Navigate } from 'react-router-dom';
import { useAuth } from '@context/AuthContext';
import LoadingSpinner from '@components/common/LoadingSpinner';

const ProtectedRoute = ({ children, permission = null, role = null }) => {
  const { user, loading, hasPermission, hasRole } = useAuth();

  // Mostrar loading mientras verifica autenticación
  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" text="Cargando..." />
      </div>
    );
  }

  // Si no está autenticado, redirect a login
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Verificar permiso si se especificó
  if (permission && !hasPermission(permission)) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">403</h1>
          <p className="text-xl text-gray-600 mb-4">
            No tienes permisos para acceder a esta página
          </p>
          <button
            onClick={() => window.history.back()}
            className="btn btn-primary"
          >
            Volver
          </button>
        </div>
      </div>
    );
  }

  // Verificar rol si se especificó
  if (role && !hasRole(role)) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">403</h1>
          <p className="text-xl text-gray-600 mb-4">
            Requiere rol: {role}
          </p>
          <button
            onClick={() => window.history.back()}
            className="btn btn-primary"
          >
            Volver
          </button>
        </div>
      </div>
    );
  }

  // Usuario autenticado y con permisos correctos
  return children;
};

export default ProtectedRoute;