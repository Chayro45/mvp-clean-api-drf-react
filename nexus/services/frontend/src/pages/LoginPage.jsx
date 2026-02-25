/**
 * pages/LoginPage.jsx
 * 
 * Página de inicio de sesión
 */

import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@context/AuthContext';
import LoginForm from '@components/auth/LoginForm';

const LoginPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  // Si ya está autenticado, redirect a dashboard
  useEffect(() => {
    if (user) {
      navigate('/dashboard');
    }
  }, [user, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        {/* Logo y título */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-primary-700 mb-2">
            Minimum API
          </h1>
          <p className="text-gray-600">
            Ingresa tus credenciales para continuar
          </p>
        </div>

        {/* Card del formulario */}
        <div className="card">
          <LoginForm />
        </div>

        {/* Footer */}
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-600">
            Proyecto de prueba - Arquitectura limpia
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
