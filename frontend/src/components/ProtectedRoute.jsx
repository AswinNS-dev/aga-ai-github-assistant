import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Layout from './Layout'

export default function ProtectedRoute({ children }) {
  const { auth } = useAuth()
  if (!auth) return <Navigate to="/auth" replace />
  return <Layout>{children}</Layout>
}
