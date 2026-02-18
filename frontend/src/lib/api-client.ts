const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

let accessToken: string | null = null

export function setAccessToken(token: string | null) {
  accessToken = token
}

export function getAccessToken(): string | null {
  return accessToken
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private async request(path: string, options: RequestInit = {}): Promise<any> {
    const headers: Record<string, string> = {
      ...((options.headers as Record<string, string>) || {}),
    }

    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`
    }

    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json'
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    if (response.status === 204) return null
    return response.json()
  }

  async get(path: string): Promise<any> {
    return this.request(path)
  }

  async post(path: string, data?: any): Promise<any> {
    return this.request(path, {
      method: 'POST',
      body: data instanceof FormData ? data : JSON.stringify(data),
    })
  }

  async patch(path: string, data: any): Promise<any> {
    return this.request(path, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async delete(path: string): Promise<any> {
    return this.request(path, { method: 'DELETE' })
  }
}

export const apiClient = new ApiClient(API_BASE)
