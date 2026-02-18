'use client'

import { useState, useCallback } from 'react'
import { apiClient } from '@/lib/api-client'
import type { Message } from '@/types/models'

export function useChat(conversationId: string) {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)

  const fetchMessages = useCallback(async () => {
    setLoading(true)
    try {
      const data = await apiClient.get(
        `/api/v1/conversations/${conversationId}/messages/`
      )
      setMessages(data.messages)
    } catch (err) {
      console.error('Failed to fetch messages:', err)
    } finally {
      setLoading(false)
    }
  }, [conversationId])

  const sendMessage = useCallback(async (content: string) => {
    setSending(true)
    try {
      const response = await apiClient.post(
        `/api/v1/conversations/${conversationId}/messages/`,
        { content }
      )
      setMessages(prev => [
        ...prev,
        { ...response, role: 'user', content } as any,
        response,
      ])
      return response
    } finally {
      setSending(false)
    }
  }, [conversationId])

  return { messages, loading, sending, fetchMessages, sendMessage }
}
