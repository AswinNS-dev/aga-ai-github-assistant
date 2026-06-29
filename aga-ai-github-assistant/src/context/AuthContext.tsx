import { createContext, useContext, useState, type ReactNode } from 'react'

interface AuthData {
  name: string
  avatar: string
  public_repos: number
  github_token: string
  groq_key: string
}

interface AuthContextType {
  auth: AuthData | null
  login: (data: AuthData) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [auth, setAuth] = useState<AuthData | null>(() => {
    const saved = sessionStorage.getItem('aga_auth')
    return saved ? (JSON.parse(saved) as AuthData) : null
  })

  const login = (data: AuthData) => {
    sessionStorage.setItem('aga_auth', JSON.stringify(data))
    setAuth(data)
  }

  const logout = () => {
    sessionStorage.removeItem('aga_auth')
    setAuth(null)
  }

  return (
    <AuthContext.Provider value={{ auth, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within an AuthProvider')
  return context
}
