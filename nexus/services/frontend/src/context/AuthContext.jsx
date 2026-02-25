/**
 * context/AuthContext.jsx
 * 
 * Context para manejar autenticación global
 * Incluye:
 * - Login/Logout
 * - Auto-refresh de tokens
 * - Detección de inactividad
 * - Sync entre tabs
 */

import { createContext, useContext, useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import authService from '@services/authService';
import useIdleTimeout from '../hooks/useIdleTimeout';
import IdleWarningModal from '@components/common/IdleWarningModal';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showIdleWarning, setShowIdleWarning] = useState(false);

  // Configuración de inactividad
  const IDLE_TIME = 10 * 60 * 1000; // 10 minutos
  const WARNING_TIME = 60; // 60 segundos de advertencia

  // Inicializar: verificar si hay usuario en localStorage
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedUser = authService.getStoredUser();
        const isAuth = authService.isAuthenticated();

        if (isAuth && storedUser) {
          // Verificar que el token sea válido
          const isValid = await authService.verifyToken();

          if (isValid) {
            // Actualizar datos del usuario desde el servidor
            const currentUser = await authService.getCurrentUser();
            setUser(currentUser);
          } else {
            // Token inválido, limpiar
            await authService.logout();
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        await authService.logout();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  // Sync entre tabs (localStorage events)
  useEffect(() => {
    const handleStorageChange = (e) => {
      // Si otra tab hizo logout
      if (e.key === 'access_token' && !e.newValue) {
        setUser(null);
        toast.info('Sesión cerrada en otra pestaña');
        window.location.href = '/login';
      }

      // Si otra tab hizo login
      if (e.key === 'user' && e.newValue) {
        const newUser = JSON.parse(e.newValue);
        setUser(newUser);
        toast.success('Sesión iniciada en otra pestaña');
      }
    };

    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  // Detección de inactividad
  const handleIdle = () => {
    if (user) {
      setShowIdleWarning(true);
    }
  };

  const handleContinue = () => {
    setShowIdleWarning(false);
    resetIdleTimer();
  };

  const handleIdleLogout = async () => {
    setShowIdleWarning(false);
    toast.info('Sesión cerrada por inactividad');
    await logout();
  };

  const { resetTimer: resetIdleTimer } = useIdleTimeout({
    onIdle: handleIdle,
    idleTime: IDLE_TIME,
  });

  /**
   * Login
   */
  const login = async (username, password) => {
    try {
      const data = await authService.login(username, password);
      setUser(data.user);
      resetIdleTimer(); // Resetear timer al hacer login
      return { success: true, user: data.user };
    } catch (error) {
      const message = error.response?.data?.detail || 'Error al iniciar sesión';
      return { success: false, error: message };
    }
  };

  /**
   * Logout
   */
  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
    }
  };

  /**
   * Actualizar usuario
   */
  const updateUser = async () => {
    try {
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      console.error('Error updating user:', error);
    }
  };

  /**
   * Verificar si el usuario tiene un permiso específico
   */
  const hasPermission = (permission) => {
    if (!user) return false;
    if (user.is_superuser) return true;
    return user.permissions?.includes(permission) || false;
  };

  /**
   * Verificar si el usuario tiene un rol específico
   */
  const hasRole = (role) => {
    if (!user) return false;
    return user.roles?.includes(role) || false;
  };

  const value = {
    user,
    loading,
    login,
    logout,
    updateUser,
    hasPermission,
    hasRole,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
      
      {/* Modal de advertencia de inactividad */}
      <IdleWarningModal
        isOpen={showIdleWarning}
        onContinue={handleContinue}
        onLogout={handleIdleLogout}
        countdown={WARNING_TIME}
      />
    </AuthContext.Provider>
  );
};

/**
 * Hook para usar el contexto de autenticación
 */
export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }

  return context;
};

export default AuthContext;
