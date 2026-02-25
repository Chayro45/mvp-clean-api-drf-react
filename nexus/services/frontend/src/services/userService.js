/**
 * services/userService.js
 * 
 * Servicio para gestión de usuarios (CRUD)
 */

import api from './api';

const userService = {
  /**
   * Listar usuarios con paginación y filtros
   * @param {object} params - Query params (page, search, etc.)
   * @returns {Promise}
   */
  async getUsers(params = {}) {
    const response = await api.get('/users/', { params });
    return response.data;
  },

  /**
   * Obtener un usuario por ID
   * @param {number} id 
   * @returns {Promise}
   */
  async getUser(id) {
    const response = await api.get(`/users/${id}/`);
    return response.data;
  },

  /**
   * Crear nuevo usuario
   * @param {object} userData 
   * @returns {Promise}
   */
  async createUser(userData) {
    const response = await api.post('/users/', userData);
    return response.data;
  },

  /**
   * Actualizar usuario
   * @param {number} id 
   * @param {object} userData 
   * @returns {Promise}
   */
  async updateUser(id, userData) {
    const response = await api.put(`/users/${id}/`, userData);
    return response.data;
  },

  /**
   * Actualización parcial de usuario
   * @param {number} id 
   * @param {object} userData 
   * @returns {Promise}
   */
  async patchUser(id, userData) {
    const response = await api.patch(`/users/${id}/`, userData);
    return response.data;
  },

  /**
   * Eliminar usuario (soft delete)
   * @param {number} id 
   * @returns {Promise}
   */
  async deleteUser(id) {
    const response = await api.delete(`/users/${id}/`);
    return response.data;
  },

  /**
   * Cambiar password de usuario
   * @param {number} id 
   * @param {object} passwordData - {old_password, new_password, new_password_confirm}
   * @returns {Promise}
   */
  async changePassword(id, passwordData) {
    const response = await api.post(`/users/${id}/change_password/`, passwordData);
    return response.data;
  },

  /**
   * Obtener grupos (roles) disponibles
   * @returns {Promise}
   */
  async getGroups() {
    const response = await api.get('/users/groups/');
    return response.data;
  },
};

export default userService;