'use client'

import { useState } from 'react'

interface MessageInputProps {
  onSend: (content: string) => void
  disabled?: boolean
}

export function MessageInput({ onSend, disabled }: MessageInputProps) {
  const [input, setInput] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() && !disabled) {
      onSend(input.trim())
      setInput('')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="border-t p-4 flex gap-2">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type a message..."
        disabled={disabled}
        className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={disabled || !input.trim()}
        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
      >
        Send
      </button>
    </form>
  )
}
