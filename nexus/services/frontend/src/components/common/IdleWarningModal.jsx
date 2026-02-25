/**
 * components/common/IdleWarningModal.jsx
 * 
 * Modal de advertencia de inactividad
 */

import { useState, useEffect } from 'react';
import Modal from './Modal';

const IdleWarningModal = ({ isOpen, onContinue, onLogout, countdown = 60 }) => {
  const [timeLeft, setTimeLeft] = useState(countdown);

  useEffect(() => {
    if (!isOpen) {
      setTimeLeft(countdown);
      return;
    }

    const interval = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          onLogout();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isOpen, countdown, onLogout]);

  if (!isOpen) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onContinue}
      title="⏱️ Sesión por expirar"
      size="sm"
    >
      <div className="text-center py-4">
        <div className="mb-4">
          <div className="text-6xl font-bold text-primary-600 mb-2">
            {timeLeft}
          </div>
          <p className="text-gray-600">
            Tu sesión expirará por inactividad
          </p>
        </div>

        <div className="space-y-3">
          <button
            onClick={onContinue}
            className="w-full btn btn-primary"
          >
            Continuar trabajando
          </button>
          <button
            onClick={onLogout}
            className="w-full btn btn-secondary"
          >
            Cerrar sesión
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default IdleWarningModal;