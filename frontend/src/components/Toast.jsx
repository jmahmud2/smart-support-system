import { useState, useEffect } from 'react';

export default function Toast({ message, type = 'success', duration = 3000, onClose }) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      onClose?.();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  if (!visible) return null;

  const bgColor = type === 'success' ? 'bg-green-50 border-green-400 text-green-800' :
                  type === 'error' ? 'bg-red-50 border-red-400 text-red-800' :
                  type === 'warning' ? 'bg-yellow-50 border-yellow-400 text-yellow-800' :
                  'bg-blue-50 border-blue-400 text-blue-800';

  return (
    <div className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-lg border ${bgColor} shadow-lg max-w-sm`}>
      <p className="text-sm">{message}</p>
    </div>
  );
}