/**
 * pages/UsersPage.jsx
 * 
 * Página de gestión de usuarios (lista, crear, editar, eliminar)
 * ACTUALIZADO: Con modals funcionando
 */

import { useState, useEffect } from 'react';
import { useAuth } from '@context/AuthContext';
import toast from 'react-hot-toast';
import Navbar from '@components/common/Navbar';
import LoadingSpinner from '@components/common/LoadingSpinner';
import UserFormModal from '@components/users/UserFormModal';
import userService from '@services/userService';

const UsersPage = () => {
  const { hasPermission } = useAuth();

  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Paginación
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Búsqueda
  const [search, setSearch] = useState('');

  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  // Grupos (roles)
  const [groups, setGroups] = useState([]);

  // Permisos
  const canCreate = hasPermission('auth.add_user');
  const canEdit = hasPermission('auth.change_user');
  const canDelete = hasPermission('auth.delete_user');

  // Cargar usuarios
  useEffect(() => {
    loadUsers();
  }, [page, search]);

  // Cargar grupos al montar
  useEffect(() => {
    loadGroups();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = {
        page,
        search: search || undefined,
      };

      const response = await userService.getUsers(params);

      setUsers(response.results || []);
      setTotalPages(Math.ceil((response.count || 0) / 20));
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cargar usuarios');
      console.error('Error loading users:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadGroups = async () => {
    try {
      const groupsData = await userService.getGroups();
      // console.log('Grupos cargados:', groupsData); // DEBUG
      setGroups(groupsData);
    } catch (err) {
      console.error('Error loading groups:', err);
      // toast.error('Error al cargar roles:' + err); // Agregar feedback
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1); // Reset a página 1 al buscar
  };

  const handleDelete = async (userId, username, isActive) => {
    if (!canDelete) {
      toast.error('No tienes permisos para inactivar usuarios');
      return;
    }

    if (!isActive) {
      toast.error('El usuario ya está inactivo');
      return;
    }

    if (!confirm(`¿Estás seguro de inactivar al usuario "${username}"?`)) {
      return;
    }

    try {
      await userService.deleteUser(userId);
      toast.success('Usuario inactivado correctamente');
      loadUsers(); // Recargar lista
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Error al inactivar usuario');
    }
  };

  const handleCreateClick = () => {
    setShowCreateModal(true);
  };

  const handleEditClick = (user) => {
    setSelectedUser(user);
    setShowEditModal(true);
  };

  const handleModalSuccess = () => {
    toast.success(showEditModal ? 'Usuario actualizado' : 'Usuario creado');
    loadUsers();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="px-4 py-6 sm:px-0">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Gestión de Usuarios
              </h1>
              <p className="mt-2 text-gray-600">
                Administra los usuarios del sistema
              </p>
            </div>

            {canCreate && (
              <button
                onClick={handleCreateClick}
                className="btn btn-primary"
              >
                + Nuevo Usuario
              </button>
            )}
          </div>
        </div>

        {/* Búsqueda */}
        <div className="px-4 sm:px-0 mb-6">
          <form onSubmit={handleSearch} className="flex gap-2">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Buscar por usuario, email, nombre..."
              className="input flex-1"
            />
            <button type="submit" className="btn btn-primary">
              Buscar
            </button>
            {search && (
              <button
                type="button"
                onClick={() => {
                  setSearch('');
                  setPage(1);
                }}
                className="btn btn-secondary"
              >
                Limpiar
              </button>
            )}
          </form>
        </div>

        {/* Contenido */}
        <div className="px-4 sm:px-0">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {loading ? (
            <div className="card flex justify-center py-12">
              <LoadingSpinner size="lg" text="Cargando usuarios..." />
            </div>
          ) : users.length === 0 ? (
            <div className="card text-center py-12">
              <p className="text-gray-500">No se encontraron usuarios</p>
            </div>
          ) : (
            <>
              {/* Tabla de usuarios */}
              <div className="card overflow-hidden p-0">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Usuario
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Email
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Roles
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Estado
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Acciones
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {users.map((user) => (
                        <tr key={user.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900">
                                {user.username}
                              </div>
                              <div className="text-sm text-gray-500">
                                {user.full_name}
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900">{user.email}</div>
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex flex-wrap gap-1">
                              {user.roles && user.roles.length > 0 ? (
                                user.roles.map((role, idx) => (
                                  <span
                                    key={idx}
                                    className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-primary-100 text-primary-800"
                                  >
                                    {role}
                                  </span>
                                ))
                              ) : (
                                <span className="text-xs text-gray-400">Sin roles</span>
                              )}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${user.is_active
                              ? 'bg-green-100 text-green-800'
                              : 'bg-red-100 text-red-800'
                              }`}>
                              {user.is_active ? 'Activo' : 'Inactivo'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <div className="flex justify-end gap-2">
                              {canEdit && (
                                <button
                                  onClick={() => handleEditClick(user)}
                                  className="text-primary-600 hover:text-primary-900"
                                >
                                  Editar
                                </button>
                              )}
                              {canDelete && (
                                <button
                                  onClick={() => handleDelete(user.id, user.username, user.is_active)}
                                  disabled={!user.is_active}
                                  className={`${user.is_active
                                    ? 'text-red-600 hover:text-red-900'
                                    : 'text-gray-400 cursor-not-allowed'
                                    }`}
                                  title={user.is_active ? 'Inactivar usuario' : 'Usuario ya inactivo'}
                                >
                                  Inactivar
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Paginación */}
              {totalPages > 1 && (
                <div className="mt-6 flex justify-center gap-2">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="btn btn-secondary disabled:opacity-50"
                  >
                    Anterior
                  </button>
                  <span className="px-4 py-2 text-gray-700">
                    Página {page} de {totalPages}
                  </span>
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="btn btn-secondary disabled:opacity-50"
                  >
                    Siguiente
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Modals */}
      <UserFormModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSuccess={handleModalSuccess}
        groups={groups}
      />

      <UserFormModal
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false);
          setSelectedUser(null);
        }}
        onSuccess={handleModalSuccess}
        user={selectedUser}
        groups={groups}
      />
    </div>
  );
};

export default UsersPage;