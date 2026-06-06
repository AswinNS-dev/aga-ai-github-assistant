import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Landing from './pages/Landing'
import Auth from './pages/Auth'
import Dashboard from './pages/Dashboard'
import RepoManager from './pages/RepoManager'
import Analyzer from './pages/Analyzer'
import ReadmeGen from './pages/ReadmeGen'
import CreateRepo from './pages/CreateRepo'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster
          position="top-right"
          toastOptions={{
            style: { background: '#161b22', color: '#fff', border: '1px solid #30363d' },
          }}
        />
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/auth" element={<Auth />} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/repo-manager" element={<ProtectedRoute><RepoManager /></ProtectedRoute>} />
          <Route path="/analyzer" element={<ProtectedRoute><Analyzer /></ProtectedRoute>} />
          <Route path="/readme" element={<ProtectedRoute><ReadmeGen /></ProtectedRoute>} />
          <Route path="/create-repo" element={<ProtectedRoute><CreateRepo /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
