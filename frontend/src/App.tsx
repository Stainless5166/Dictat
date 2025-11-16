import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import Login from '@/pages/Login';
import Register from '@/pages/Register';
import Dashboard from '@/pages/Dashboard';
import DoctorDashboard from '@/pages/DoctorDashboard';
import DictationUpload from '@/pages/DictationUpload';
import SecretaryWorkQueue from '@/pages/SecretaryWorkQueue';
import MyWork from '@/pages/MyWork';
import TranscriptionEditor from '@/pages/TranscriptionEditor';
import { UserRole } from '@/types/api-types';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />

          {/* Doctor routes */}
          <Route
            path="/doctor/dashboard"
            element={
              <ProtectedRoute allowedRoles={[UserRole.DOCTOR, UserRole.ADMIN]}>
                <DoctorDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dictations"
            element={
              <ProtectedRoute allowedRoles={[UserRole.DOCTOR, UserRole.ADMIN]}>
                <DoctorDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/upload"
            element={
              <ProtectedRoute allowedRoles={[UserRole.DOCTOR, UserRole.ADMIN]}>
                <DictationUpload />
              </ProtectedRoute>
            }
          />

          {/* Secretary routes */}
          <Route
            path="/queue"
            element={
              <ProtectedRoute allowedRoles={[UserRole.SECRETARY, UserRole.ADMIN]}>
                <SecretaryWorkQueue />
              </ProtectedRoute>
            }
          />
          <Route
            path="/my-work"
            element={
              <ProtectedRoute allowedRoles={[UserRole.SECRETARY, UserRole.ADMIN]}>
                <MyWork />
              </ProtectedRoute>
            }
          />
          <Route
            path="/transcribe/:id"
            element={
              <ProtectedRoute allowedRoles={[UserRole.SECRETARY, UserRole.ADMIN]}>
                <TranscriptionEditor />
              </ProtectedRoute>
            }
          />

          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />

          {/* 404 */}
          <Route
            path="*"
            element={
              <div className="flex min-h-screen items-center justify-center">
                <div className="text-center">
                  <h1 className="text-4xl font-bold text-gray-900">404</h1>
                  <p className="mt-2 text-gray-600">Page not found</p>
                </div>
              </div>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
