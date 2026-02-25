/**
 * services/api.js
 * 
 * Configuración base de Axios con interceptores para:
 * - Agregar JWT token automáticamente
 * - Refresh automático de access token
 * - Manejo de errores centralizado
 * - Toast de feedback (solo en dev)
 */

import axios from 'axios';
import toast from 'react-hot-toast';

// Base URL del API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const IS_DEV = import.meta.env.DEV;

// Crear instancia de Axios
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Variable para evitar múltiples refreshes simultáneos
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

// Interceptor de Request - Agregar token JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor de Response - Refresh token automático
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Si es error de red (backend caído)
    if (!error.response) {
      toast.error('Error de conexión. Verifica tu internet.');
      return Promise.reject(error);
    }

    // Si es 401 y no hemos intentado refresh aún
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Ya hay un refresh en progreso, agregar a la cola
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');

        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        // Intentar refresh
        const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;

        // Guardar nuevo access token
        localStorage.setItem('access_token', access);

        // Toast solo en desarrollo
        if (IS_DEV) {
          toast.success('Sesión renovada automáticamente', {
            duration: 2000,
            icon: '🔄',
          });
        }

        // Procesar cola de requests que estaban esperando
        processQueue(null, access);

        // Reintentar request original con nuevo token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);

      } catch (refreshError) {
        // Refresh falló (token expirado o inválido)
        processQueue(refreshError, null);
        
        // Limpiar storage
        localStorage.clear();
        
        // Toast de sesión expirada
        toast.error('Tu sesión ha expirado. Redirigiendo...', {
          duration: 2000,
        });

        // Redirect después de 2 segundos
        setTimeout(() => {
          window.location.href = '/login';
        }, 2000);

        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;