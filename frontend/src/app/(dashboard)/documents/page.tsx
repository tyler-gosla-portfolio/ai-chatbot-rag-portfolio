'use client'

import { useState, useEffect } from 'react'
import { UploadDropzone } from '@/components/documents/UploadDropzone'
import { DocumentTable } from '@/components/documents/DocumentTable'
import { apiClient } from '@/lib/api-client'
import type { Document } from '@/types/models'

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)

  const fetchDocuments = async () => {
    try {
      const data = await apiClient.get('/api/v1/documents/')
      setDocuments(data.documents)
    } catch (err) {
      console.error('Failed to fetch documents:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [])

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Documents</h1>
      <UploadDropzone onUploadComplete={fetchDocuments} />
      {loading ? (
        <p className="text-gray-500 mt-4">Loading documents...</p>
      ) : (
        <DocumentTable documents={documents} onDelete={fetchDocuments} />
      )}
    </div>
  )
}
