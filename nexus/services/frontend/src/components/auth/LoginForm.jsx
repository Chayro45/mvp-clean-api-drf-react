/**
 * components/auth/LoginForm.jsx
 * 
 * Formulario de login con validación
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@context/AuthContext';

const LoginForm = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    
    // Limpiar error del campo al escribir
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.username.trim()) {
      newErrors.username = 'El usuario es requerido';
    }

    if (!formData.password) {
      newErrors.password = 'La contraseña es requerida';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validate()) return;

    setLoading(true);
    setErrors({});

    try {
      const result = await login(formData.username, formData.password);

      if (result.success) {
        // Redirect a dashboard
        navigate('/dashboard');
      } else {
        // Mostrar error
        setErrors({ submit: result.error });
      }
    } catch (error) {
      setErrors({ 
        submit: 'Error de conexión. Por favor intenta de nuevo.' 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Error general */}
      {errors.submit && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
          {errors.submit}
        </div>
      )}

      {/* Username */}
      <div>
        <label htmlFor="username" className="label">
          Usuario
        </label>
        <input
          type="text"
          id="username"
          name="username"
          value={formData.username}
          onChange={handleChange}
          className={`input ${errors.username ? 'input-error' : ''}`}
          placeholder="Ingresa tu usuario"
          disabled={loading}
        />
        {errors.username && (
          <p className="error-message">{errors.username}</p>
        )}
      </div>

      {/* Password */}
      <div>
        <label htmlFor="password" className="label">
          Contraseña
        </label>
        <input
          type="password"
          id="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          className={`input ${errors.password ? 'input-error' : ''}`}
          placeholder="Ingresa tu contraseña"
          disabled={loading}
        />
        {errors.password && (
          <p className="error-message">{errors.password}</p>
        )}
      </div>

      {/* Submit button */}
      <button
        type="submit"
        disabled={loading}
        className="w-full btn btn-primary"
      >
        {loading ? (
          <span className="flex items-center justify-center">
            <div className="spinner w-5 h-5 mr-2"></div>
            Iniciando sesión...
          </span>
        ) : (
          'Iniciar Sesión'
        )}
      </button>

      {/* Credenciales de desarrollo */}
      {import.meta.env.DEV && (
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800 font-medium mb-2">
            Credenciales de desarrollo:
          </p>
          <p className="text-sm text-yellow-700">
            Usuario: <code className="bg-yellow-100 px-1 rounded">admin</code>
            <br />
            Contraseña: <code className="bg-yellow-100 px-1 rounded">admin</code>
          </p>
        </div>
      )}
    </form>
  );
};

export default LoginForm;
