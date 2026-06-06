import { createContext, useContext, useState } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(() => {
    const saved = sessionStorage.getItem('aga_auth')
    return saved ? JSON.parse(saved) : null
  })

  const login = (data) => {
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

export const useAuth = () => useContext(AuthContext)
