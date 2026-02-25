/**
 * utils/errorMessages.js
 * 
 * Helper para convertir errores técnicos del backend en mensajes amigables
 */

const ERROR_MESSAGES = {
  // Errores comunes de Django/DRF
  'This field is required.': 'Este campo es requerido',
  'This field may not be blank.': 'Este campo no puede estar vacío',
  'This field may not be null.': 'Este campo es requerido',
  'Enter a valid email address.': 'Ingresa un email válido',
  'Ensure this field has no more than': 'El texto es demasiado largo',
  'Ensure this field has at least': 'El texto es demasiado corto',
  
  // Errores de usuario
  'A user with that username already exists.': 'Este nombre de usuario ya existe',
  'user with this username already exists.': 'Este nombre de usuario ya existe',
  'User with this email already exists': 'Este email ya está registrado',
  
  // Errores de autenticación
  'Invalid credentials': 'Usuario o contraseña incorrectos',
  'Unable to log in with provided credentials.': 'Usuario o contraseña incorrectos',
  'No active account found with the given credentials': 'Usuario o contraseña incorrectos',
  
  // Errores de password
  'This password is too short.': 'La contraseña es demasiado corta (mínimo 8 caracteres)',
  'This password is too common.': 'Elige una contraseña más segura',
  'This password is entirely numeric.': 'La contraseña no puede ser solo números',
  'The two password fields didn\'t match.': 'Las contraseñas no coinciden',
  
  // Errores de permisos
  'You do not have permission': 'No tienes permisos para realizar esta acción',
  'Authentication credentials were not provided.': 'Debes iniciar sesión',
  'Invalid token': 'Tu sesión ha expirado',
  
  // Errores de validación
  'Invalid pk': 'Registro no encontrado',
  'Not found.': 'No encontrado',
  'Method not allowed': 'Operación no permitida',
};

/**
 * Formatea un error del backend a mensaje amigable
 * @param {any} error - Error de axios
 * @returns {string} - Mensaje amigable
 */
export const formatErrorMessage = (error) => {
  // Si no hay response, es error de red
  if (!error.response) {
    return 'Error de conexión. Verifica tu internet.';
  }

  const errorData = error.response.data;

  // Si es un string simple
  if (typeof errorData === 'string') {
    return findFriendlyMessage(errorData) || 'Ocurrió un error. Intenta de nuevo.';
  }

  // Si es un objeto con campos
  if (typeof errorData === 'object' && errorData !== null) {
    // Si tiene campo 'detail'
    if (errorData.detail) {
      return findFriendlyMessage(errorData.detail) || errorData.detail;
    }

    // Si tiene errores de campo
    const firstKey = Object.keys(errorData)[0];
    if (firstKey) {
      const fieldError = errorData[firstKey];
      const errorText = Array.isArray(fieldError) ? fieldError[0] : fieldError;
      
      // Intentar encontrar mensaje amigable
      const friendlyMessage = findFriendlyMessage(errorText);
      if (friendlyMessage) {
        return friendlyMessage;
      }

      // Si no hay mensaje amigable, formatear genérico
      const fieldName = formatFieldName(firstKey);
      return `${fieldName}: ${errorText}`;
    }
  }

  // Fallback genérico
  return 'Ocurrió un error al guardar. Por favor intenta de nuevo.';
};

/**
 * Busca un mensaje amigable en el diccionario
 */
const findFriendlyMessage = (errorText) => {
  if (!errorText) return null;

  // Buscar coincidencia exacta
  if (ERROR_MESSAGES[errorText]) {
    return ERROR_MESSAGES[errorText];
  }

  // Buscar coincidencia parcial
  for (const [key, value] of Object.entries(ERROR_MESSAGES)) {
    if (errorText.includes(key)) {
      return value;
    }
  }

  return null;
};

/**
 * Formatea nombre de campo técnico a legible
 */
const formatFieldName = (fieldName) => {
  const fieldNames = {
    'username': 'Usuario',
    'email': 'Email',
    'password': 'Contraseña',
    'first_name': 'Nombre',
    'last_name': 'Apellido',
    'phone': 'Teléfono',
    'department': 'Departamento',
    'employee_id': 'ID Empleado',
    'group_ids': 'Roles',
    'is_active': 'Estado',
  };

  return fieldNames[fieldName] || fieldName;
};

export default formatErrorMessage;