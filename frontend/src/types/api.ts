import type { Document, Conversation, Message } from './models'

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface DocumentListResponse {
  documents: Document[]
  total: number
  page: number
  page_size: number
}

export interface ConversationListResponse {
  conversations: Conversation[]
  total: number
}

export interface MessageListResponse {
  messages: Message[]
  has_more: boolean
}
