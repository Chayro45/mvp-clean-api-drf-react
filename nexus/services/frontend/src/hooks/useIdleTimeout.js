/**
 * hooks/useIdleTimeout.js
 * 
 * Hook para detectar inactividad del usuario
 */

import { useEffect, useRef, useCallback } from 'react';

const useIdleTimeout = ({ onIdle, idleTime = 15 * 60 * 1000 }) => {
  const timeoutId = useRef(null);
  const warningTimeoutId = useRef(null);

  const resetTimer = useCallback(() => {
    // Limpiar timers existentes
    if (timeoutId.current) clearTimeout(timeoutId.current);
    if (warningTimeoutId.current) clearTimeout(warningTimeoutId.current);

    // Configurar nuevo timer
    timeoutId.current = setTimeout(() => {
      onIdle();
    }, idleTime);
  }, [onIdle, idleTime]);

  useEffect(() => {
    // Eventos que resetean el timer
    const events = [
      'mousedown',
      'mousemove',
      'keypress',
      'scroll',
      'touchstart',
      'click',
    ];

    // Agregar listeners
    events.forEach((event) => {
      document.addEventListener(event, resetTimer, true);
    });

    // Iniciar timer
    resetTimer();

    // Cleanup
    return () => {
      events.forEach((event) => {
        document.removeEventListener(event, resetTimer, true);
      });
      if (timeoutId.current) clearTimeout(timeoutId.current);
      if (warningTimeoutId.current) clearTimeout(warningTimeoutId.current);
    };
  }, [resetTimer]);

  return { resetTimer };
};

export default useIdleTimeout;