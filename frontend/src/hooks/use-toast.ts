import { useState } from 'react';

interface Toast {
  title: string;
  description?: string;
  variant?: 'default' | 'destructive';
}

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const toast = (toast: Toast) => {
    // For now, just console log
    // In a real app, this would show a toast notification
    console.log(`[${toast.variant || 'default'}] ${toast.title}: ${toast.description || ''}`);
    
    // You could also use a library like react-hot-toast or sonner
    // Example with react-hot-toast:
    // import toast from 'react-hot-toast';
    // if (toast.variant === 'destructive') {
    //   toast.error(`${toast.title}: ${toast.description}`);
    // } else {
    //   toast.success(`${toast.title}: ${toast.description}`);
    // }
  };

  return { toast };
}