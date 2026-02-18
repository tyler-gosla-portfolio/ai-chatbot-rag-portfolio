export interface User {
  id: string
  email: string
  display_name: string | null
  is_active: boolean
  created_at: string
}

export interface Document {
  id: string
  title: string
  filename: string
  mime_type: string
  file_size_bytes: number
  status: 'pending' | 'processing' | 'ready' | 'failed'
  error_message: string | null
  chunk_count: number
  created_at: string
  updated_at: string
}

export interface Conversation {
  id: string
  title: string | null
  model: string
  system_prompt: string | null
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  conversation_id: string
  role: 'system' | 'user' | 'assistant'
  content: string
  token_count: number | null
  latency_ms: number | null
  model: string | null
  sources: SourceInfo[]
  feedback: number | null
  created_at: string
}

export interface SourceInfo {
  document_id: string
  chunk_index: number
  content_preview: string
  similarity: number
}
