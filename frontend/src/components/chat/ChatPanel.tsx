'use client'

import { useEffect, useState } from 'react'
import { useChat } from '@/hooks/useChat'
import { MessageBubble } from './MessageBubble'
import { MessageInput } from './MessageInput'

interface ChatPanelProps {
  conversationId: string
}

export function ChatPanel({ conversationId }: ChatPanelProps) {
  const { messages, loading, sending, fetchMessages, sendMessage } = useChat(conversationId)

  useEffect(() => {
    fetchMessages()
  }, [fetchMessages])

  const handleSend = async (content: string) => {
    await sendMessage(content)
    await fetchMessages()
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {loading ? (
          <p className="text-gray-500 text-center">Loading messages...</p>
        ) : messages.length === 0 ? (
          <p className="text-gray-500 text-center">No messages yet. Start the conversation!</p>
        ) : (
          messages.map((msg) => <MessageBubble key={msg.id} message={msg} />)
        )}
        {sending && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-2 text-gray-500">
              Thinking...
            </div>
          </div>
        )}
      </div>
      <MessageInput onSend={handleSend} disabled={sending} />
    </div>
  )
}
