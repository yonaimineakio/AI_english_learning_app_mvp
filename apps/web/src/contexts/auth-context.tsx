"use client"

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'

interface User {
  id: string
  name: string
  email: string
  picture?: string
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: () => void
  logout: () => void
  token: string | null
  setAuthData: (token: string, user: User) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps): JSX.Element {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [token, setToken] = useState<string | null>(null)

  const isAuthenticated = !!user && !!token

  // 初期化時にトークンをチェック
  useEffect(() => {
    const initAuth = () => {
      try {
        const storedToken = localStorage.getItem('access_token')
        const storedUser = localStorage.getItem('user')
        
        if (storedToken && storedUser) {
          setToken(storedToken)
          setUser(JSON.parse(storedUser))
          setIsLoading(false)
          return
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error)
        // エラー時は認証情報をクリア
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
      }

      setIsLoading(false)
    }

    initAuth()
  }, [])

  const setAuthData = (accessToken: string, authUser: User) => {
    setToken(accessToken)
    setUser(authUser)
    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('user', JSON.stringify(authUser))
    setIsLoading(false)
  }

  const login = () => {
    // Googleログイン処理
    const apiBaseUrl = (process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '')
    window.location.href = `${apiBaseUrl}/auth/login`
  }

  const logout = () => {
    // 認証情報をクリア
    setUser(null)
    setToken(null)
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    setIsLoading(false)
    
    // ログアウト処理
    const apiBaseUrl = (process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '')
    const returnTo = encodeURIComponent(window.location.origin)

    window.location.href = `${apiBaseUrl}/auth/logout?return_to=${returnTo}`
  }

  // トークン期限切れチェック
  useEffect(() => {
    if (!token) return

    const checkTokenExpiry = () => {
      try {
        // モックトークンの場合は期限チェックをスキップ
        if (token.startsWith('mock_jwt_token_')) {
          return
        }
        
        // JWTトークンの期限をチェック（簡易実装）
        const payload = JSON.parse(atob(token.split('.')[1]))
        const expiry = payload.exp * 1000 // expは秒単位なのでミリ秒に変換
        
        if (Date.now() >= expiry) {
          logout()
        }
      } catch (error) {
        console.error('Failed to check token expiry:', error)
        // モックトークンの場合は期限切れでログアウトしない
        if (!token.startsWith('mock_jwt_token_')) {
          logout()
        }
      }
    }

    // 5分ごとにトークン期限をチェック
    const interval = setInterval(checkTokenExpiry, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [token])

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    token,
    setAuthData,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
