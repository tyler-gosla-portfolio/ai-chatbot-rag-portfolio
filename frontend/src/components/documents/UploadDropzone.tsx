'use client'

import { useState, useRef } from 'react'
import { apiClient } from '@/lib/api-client'

interface UploadDropzoneProps {
  onUploadComplete: () => void
}

export function UploadDropzone({ onUploadComplete }: UploadDropzoneProps) {
  const [dragging, setDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleUpload = async (file: File) => {
    setUploading(true)
    setError('')
    try {
      const formData = new FormData()
      formData.append('file', file)
      await apiClient.post('/api/v1/documents/', formData)
      onUploadComplete()
    } catch (err: any) {
      setError(err.message || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleUpload(file)
  }

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
      className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition ${
        dragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
      }`}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.txt,.md,.docx"
        onChange={(e) => e.target.files?.[0] && handleUpload(e.target.files[0])}
        className="hidden"
      />
      {uploading ? (
        <p className="text-gray-500">Uploading...</p>
      ) : (
        <>
          <p className="text-gray-600 font-medium">Drop a file here or click to upload</p>
          <p className="text-sm text-gray-400 mt-1">PDF, TXT, MD, DOCX (max 10MB)</p>
        </>
      )}
      {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
    </div>
  )
}
