/**
 * components/common/LoadingSpinner.jsx
 * 
 * Spinner de carga reutilizable
 */

const LoadingSpinner = ({ size = 'md', text = '' }) => {
  const sizes = {
    sm: 'w-6 h-6',
    md: 'w-10 h-10',
    lg: 'w-16 h-16',
  };

  return (
    <div className="flex flex-col items-center justify-center">
      <div className={`spinner ${sizes[size]}`}></div>
      {text && (
        <p className="mt-3 text-gray-600">{text}</p>
      )}
    </div>
  );
};

export default LoadingSpinner;