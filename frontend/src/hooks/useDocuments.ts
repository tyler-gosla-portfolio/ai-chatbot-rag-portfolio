'use client'

import { useState, useCallback } from 'react'
import { apiClient } from '@/lib/api-client'
import type { Document } from '@/types/models'

export function useDocuments() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(false)

  const fetchDocuments = useCallback(async () => {
    setLoading(true)
    try {
      const data = await apiClient.get('/api/v1/documents/')
      setDocuments(data.documents)
    } catch (err) {
      console.error('Failed to fetch documents:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  const uploadDocument = useCallback(async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const result = await apiClient.post('/api/v1/documents/', formData)
    await fetchDocuments()
    return result
  }, [fetchDocuments])

  const deleteDocument = useCallback(async (id: string) => {
    await apiClient.delete(`/api/v1/documents/${id}`)
    await fetchDocuments()
  }, [fetchDocuments])

  return { documents, loading, fetchDocuments, uploadDocument, deleteDocument }
}
