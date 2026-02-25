/**
 * services/authService.js
 * 
 * Servicio para autenticación (login, logout, etc.)
 */

import api from './api';

const authService = {
  /**
   * Login con username y password
   * @param {string} username 
   * @param {string} password 
   * @returns {Promise} User data + tokens
   */
  async login(username, password) {
    const response = await api.post('/auth/login/', {
      username,
      password,
    });

    const { access, refresh, user } = response.data;

    // Guardar tokens en localStorage
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    localStorage.setItem('user', JSON.stringify(user));

    return response.data;
  },

  /**
   * Logout (blacklist refresh token)
   * @returns {Promise}
   */
  async logout() {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      
      if (refreshToken) {
        await api.post('/auth/logout/', {
          refresh: refreshToken,
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Limpiar localStorage siempre
      localStorage.clear();
    }
  },

  /**
   * Obtener usuario actual desde el token
   * @returns {Promise} User data
   */
  async getCurrentUser() {
    const response = await api.get('/auth/me/');
    
    // Actualizar user en localStorage
    localStorage.setItem('user', JSON.stringify(response.data));
    
    return response.data;
  },

  /**
   * Verificar si el token es válido
   * @returns {Promise<boolean>}
   */
  async verifyToken() {
    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) return false;

      await api.post('/auth/verify/', { token });
      return true;
    } catch (error) {
      return false;
    }
  },

  /**
   * Obtener usuario guardado en localStorage
   * @returns {object|null}
   */
  getStoredUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  /**
   * Verificar si el usuario está autenticado
   * @returns {boolean}
   */
  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  },
};

export default authService;