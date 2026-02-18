import type { Document } from '@/types/models'
import { formatFileSize, formatDate } from '@/lib/format'
import { apiClient } from '@/lib/api-client'

interface DocumentTableProps {
  documents: Document[]
  onDelete: () => void
}

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  processing: 'bg-blue-100 text-blue-800',
  ready: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
}

export function DocumentTable({ documents, onDelete }: DocumentTableProps) {
  const handleDelete = async (id: string) => {
    try {
      await apiClient.delete(`/api/v1/documents/${id}`)
      onDelete()
    } catch (err) {
      console.error('Failed to delete:', err)
    }
  }

  if (documents.length === 0) {
    return <p className="text-gray-500 mt-4">No documents uploaded yet.</p>
  }

  return (
    <div className="mt-6 overflow-x-auto">
      <table className="w-full text-left">
        <thead>
          <tr className="border-b">
            <th className="py-2 px-3 font-medium text-gray-600">Name</th>
            <th className="py-2 px-3 font-medium text-gray-600">Size</th>
            <th className="py-2 px-3 font-medium text-gray-600">Status</th>
            <th className="py-2 px-3 font-medium text-gray-600">Chunks</th>
            <th className="py-2 px-3 font-medium text-gray-600">Uploaded</th>
            <th className="py-2 px-3 font-medium text-gray-600"></th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <tr key={doc.id} className="border-b hover:bg-gray-50">
              <td className="py-2 px-3">{doc.filename}</td>
              <td className="py-2 px-3 text-sm">{formatFileSize(doc.file_size_bytes)}</td>
              <td className="py-2 px-3">
                <span className={`text-xs px-2 py-1 rounded-full ${statusColors[doc.status]}`}>
                  {doc.status}
                </span>
              </td>
              <td className="py-2 px-3 text-sm">{doc.chunk_count}</td>
              <td className="py-2 px-3 text-sm">{formatDate(doc.created_at)}</td>
              <td className="py-2 px-3">
                <button
                  onClick={() => handleDelete(doc.id)}
                  className="text-red-500 hover:text-red-700 text-sm"
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
