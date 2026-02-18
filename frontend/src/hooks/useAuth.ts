'use client'

import { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient, setAccessToken } from '@/lib/api-client'
import type { User } from '@/types/models'
import type { TokenResponse } from '@/types/api'

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const login = useCallback(async (email: string, password: string) => {
    setLoading(true)
    try {
      const data: TokenResponse = await apiClient.post('/api/v1/auth/login', { email, password })
      setAccessToken(data.access_token)
      const userData = await apiClient.get('/api/v1/auth/me')
      setUser(userData)
      router.push('/')
    } finally {
      setLoading(false)
    }
  }, [router])

  const register = useCallback(async (email: string, password: string, displayName?: string) => {
    setLoading(true)
    try {
      await apiClient.post('/api/v1/auth/register', {
        email,
        password,
        display_name: displayName,
      })
      await login(email, password)
    } finally {
      setLoading(false)
    }
  }, [login])

  const logout = useCallback(() => {
    setAccessToken(null)
    setUser(null)
    router.push('/login')
  }, [router])

  return { user, loading, login, register, logout }
}
