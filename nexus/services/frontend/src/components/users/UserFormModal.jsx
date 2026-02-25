/**
 * components/users/UserFormModal.jsx
 * 
 * Modal para crear o editar usuario
 */

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import Modal from '@components/common/Modal';
import LoadingSpinner from '@components/common/LoadingSpinner';
import userService from '@services/userService';

const UserFormModal = ({ isOpen, onClose, onSuccess, user = null, groups = [] }) => {
  const isEdit = !!user;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
  } = useForm({
    defaultValues: {
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      password: '',
      password_confirm: '',
      phone: '',
      department: '',
      employee_id: '',
      group_ids: [],
      is_active: true,
    },
  });

  // Cargar datos del usuario al editar
  useEffect(() => {
    if (isEdit && user) {
      reset({
        username: user.username,
        email: user.email,
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone: user.profile?.phone || '',
        department: user.profile?.department || '',
        employee_id: user.profile?.employee_id || '',
        group_ids: user.groups?.map(g => g.id) || [],
        is_active: user.is_active,
      });
    } else {
      reset({
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        password: '',
        password_confirm: '',
        phone: '',
        department: '',
        employee_id: '',
        group_ids: [],
        is_active: true,
      });
    }
  }, [isEdit, user, reset]);

  const onSubmit = async (data) => {
    setLoading(true);
    setError(null);

    try {
      // Convertir group_ids a números
      const formData = {
        ...data,
        group_ids: data.group_ids ? data.group_ids.map(id => parseInt(id)) : [],
      };

      if (isEdit) {
        // Editar usuario
        const { password, password_confirm, username, ...updateData } = formData;
        await userService.updateUser(user.id, updateData);
      } else {
        // Crear usuario
        await userService.createUser(formData);
      }

      onSuccess();
      onClose();
    } catch (err) {
      console.error('Error al guardar usuario:', err);
      
      // Usar helper de mensajes amigables
      const friendlyMessage = formatErrorMessage(err);
      setError(friendlyMessage);
    } finally {
      setLoading(false);
    }
  };

  // Validación de password match (solo al crear)
  const password = watch('password');
  
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEdit ? 'Editar Usuario' : 'Crear Usuario'}
      size="lg"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Error general */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Grid de 2 columnas */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Username */}
          <div>
            <label htmlFor="username" className="label">
              Usuario <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="username"
              disabled={isEdit} // No se puede cambiar username
              className={`input ${errors.username ? 'input-error' : ''} ${isEdit ? 'bg-gray-100' : ''}`}
              {...register('username', {
                required: 'El usuario es requerido',
                minLength: { value: 3, message: 'Mínimo 3 caracteres' },
                pattern: {
                  value: /^[a-zA-Z0-9_]+$/,
                  message: 'Solo letras, números y guión bajo',
                },
              })}
            />
            {errors.username && (
              <p className="error-message">{errors.username.message}</p>
            )}
          </div>

          {/* Email */}
          <div>
            <label htmlFor="email" className="label">
              Email <span className="text-red-500">*</span>
            </label>
            <input
              type="email"
              id="email"
              className={`input ${errors.email ? 'input-error' : ''}`}
              {...register('email', {
                required: 'El email es requerido',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Email inválido',
                },
              })}
            />
            {errors.email && (
              <p className="error-message">{errors.email.message}</p>
            )}
          </div>

          {/* First Name */}
          <div>
            <label htmlFor="first_name" className="label">
              Nombre
            </label>
            <input
              type="text"
              id="first_name"
              className={`input ${errors.first_name ? 'input-error' : ''}`}
              {...register('first_name')}
            />
          </div>

          {/* Last Name */}
          <div>
            <label htmlFor="last_name" className="label">
              Apellido
            </label>
            <input
              type="text"
              id="last_name"
              className={`input ${errors.last_name ? 'input-error' : ''}`}
              {...register('last_name')}
            />
          </div>

          {/* Password (solo al crear) */}
          {!isEdit && (
            <>
              <div>
                <label htmlFor="password" className="label">
                  Contraseña <span className="text-red-500">*</span>
                </label>
                <input
                  type="password"
                  id="password"
                  className={`input ${errors.password ? 'input-error' : ''}`}
                  {...register('password', {
                    required: 'La contraseña es requerida',
                    minLength: { value: 8, message: 'Mínimo 8 caracteres' },
                  })}
                />
                {errors.password && (
                  <p className="error-message">{errors.password.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="password_confirm" className="label">
                  Confirmar Contraseña <span className="text-red-500">*</span>
                </label>
                <input
                  type="password"
                  id="password_confirm"
                  className={`input ${errors.password_confirm ? 'input-error' : ''}`}
                  {...register('password_confirm', {
                    required: 'Confirma la contraseña',
                    validate: (value) =>
                      value === password || 'Las contraseñas no coinciden',
                  })}
                />
                {errors.password_confirm && (
                  <p className="error-message">{errors.password_confirm.message}</p>
                )}
              </div>
            </>
          )}

          {/* Phone */}
          <div>
            <label htmlFor="phone" className="label">
              Teléfono
            </label>
            <input
              type="text"
              id="phone"
              className="input"
              {...register('phone')}
            />
          </div>

          {/* Department */}
          <div>
            <label htmlFor="department" className="label">
              Departamento
            </label>
            <input
              type="text"
              id="department"
              className="input"
              {...register('department')}
            />
          </div>

          {/* Employee ID */}
          <div>
            <label htmlFor="employee_id" className="label">
              ID Empleado
            </label>
            <input
              type="text"
              id="employee_id"
              className="input"
              {...register('employee_id')}
            />
          </div>

          {/* Roles (grupos) */}
          {/* <div>
          <label htmlFor="group_ids" className="label">
              Roles
          </label>
          <select
              id="group_ids"
              multiple
              className="input h-24"
              {...register('group_ids')}
          >
              {groups.map((group) => (
              <option key={group.id} value={group.id}>
                  {group.name}
              </option>
              ))}
          </select>
          <p className="text-xs text-gray-500 mt-1">
              Mantén Ctrl/Cmd para seleccionar múltiples
          </p>
          </div> */}
          {/* Roles (grupos) - VERSIÓN MEJORADA CON CHECKBOXES */}
          {/* <div className="md:col-span-2">
          <label className="label">
              Roles
          </label>
          <div className="border border-gray-300 rounded-lg p-4 space-y-2 bg-gray-50">
              {groups.length > 0 ? (
              groups.map((group) => (
                  <div key={group.id} className="flex items-center">
                  <input
                      type="checkbox"
                      id={`group_${group.id}`}
                      value={group.id}
                      className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                      {...register('group_ids')}
                  />
                  <label
                      htmlFor={`group_${group.id}`}
                      className="ml-2 text-sm text-gray-700 cursor-pointer"
                  >
                      {group.name}
                  </label>
                  </div>
              ))
              ) : (
              <p className="text-sm text-gray-500">No hay roles disponibles</p>
              )}
          </div>
          </div> */}
          {/* Roles (grupos) - VERSIÓN CORREGIDA PARA MÚLTIPLES */}
          <div className="md:col-span-2">
            <label className="label">
              Roles
            </label>
            <div className="border border-gray-300 rounded-lg p-4 space-y-2 bg-gray-50">
              {groups.length > 0 ? (
                groups.map((group) => {
                  const { onChange, ...registerProps } = register('group_ids');
                  
                  return (
                    <div key={group.id} className="flex items-center">
                      <input
                        type="checkbox"
                        id={`group_${group.id}`}
                        value={group.id}
                        className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                        {...registerProps}
                        onChange={(e) => {
                          const currentValues = watch('group_ids') || [];
                          const value = parseInt(e.target.value);
                          
                          let newValues;
                          if (e.target.checked) {
                            // Agregar si no existe
                            newValues = currentValues.includes(value) 
                              ? currentValues 
                              : [...currentValues, value];
                          } else {
                            // Remover
                            newValues = currentValues.filter(id => id !== value);
                          }
                          
                          onChange({
                            target: {
                              name: 'group_ids',
                              value: newValues,
                            },
                          });
                        }}
                        checked={watch('group_ids')?.includes(group.id) || false}
                      />
                      <label
                        htmlFor={`group_${group.id}`}
                        className="ml-2 text-sm text-gray-700 cursor-pointer"
                      >
                        {group.name}
                      </label>
                    </div>
                  );
                })
              ) : (
                <p className="text-sm text-gray-500">Cargando roles...</p>
              )}
            </div>
          </div>

          {/* Is Active */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_active"
              className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
              {...register('is_active')}
            />
            <label htmlFor="is_active" className="ml-2 text-sm text-gray-700">
              Usuario activo
            </label>
          </div>
        </div>

        {/* Botones */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="btn btn-secondary"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary min-w-[120px]"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <div className="spinner w-5 h-5 mr-2"></div>
                Guardando...
              </span>
            ) : (
              isEdit ? 'Actualizar' : 'Crear'
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default UserFormModal;