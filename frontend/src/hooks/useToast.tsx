import { useState, useCallback } from 'react';
import Toast, { ToastType } from '@/components/Toast';

interface ToastMessage {
  id: number;
  message: string;
  type: ToastType;
}

export function useToast() {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const showToast = useCallback((message: string, type: ToastType = 'info') => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
  }, []);

  const removeToast = useCallback((id: number) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const ToastContainer = useCallback(
    () => (
      <div className="pointer-events-none fixed bottom-0 right-0 z-50 flex flex-col items-end space-y-4 p-6">
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            message={toast.message}
            type={toast.type}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </div>
    ),
    [toasts, removeToast]
  );

  return { showToast, ToastContainer };
}
