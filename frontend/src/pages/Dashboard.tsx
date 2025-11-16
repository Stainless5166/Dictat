import { Navigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { UserRole } from '@/types/api-types';

export default function Dashboard() {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Route based on user role
  if (user.role === UserRole.DOCTOR) {
    return <Navigate to="/doctor/dashboard" replace />;
  } else if (user.role === UserRole.SECRETARY) {
    return <Navigate to="/queue" replace />;
  } else if (user.role === UserRole.ADMIN) {
    return <Navigate to="/admin/dashboard" replace />;
  }

  return <Navigate to="/login" replace />;
}
