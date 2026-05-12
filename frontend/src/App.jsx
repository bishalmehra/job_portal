import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import AuthPage from './pages/AuthPage'
import HostDashboard from './pages/HostDashboard'
import UserDashboard from './pages/UserDashboard'

function ProtectedRoute({ children, role }) {
  const { user, token } = useAuth()
  if (!token || !user) return <Navigate to="/login" replace />
  if (role && user.role !== role) {
    return <Navigate to={user.role === 'host' ? '/host' : '/jobs'} replace />
  }
  return children
}

function RootRedirect() {
  const { user, token } = useAuth()
  if (!token || !user) return <Navigate to="/login" replace />
  return <Navigate to={user.role === 'host' ? '/host' : '/jobs'} replace />
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login"   element={<AuthPage mode="login" />} />
          <Route path="/signup"  element={<AuthPage mode="signup" />} />
          <Route path="/jobs"    element={<ProtectedRoute role="user"><UserDashboard /></ProtectedRoute>} />
          <Route path="/host"    element={<ProtectedRoute role="host"><HostDashboard /></ProtectedRoute>} />
          <Route path="*"        element={<RootRedirect />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}