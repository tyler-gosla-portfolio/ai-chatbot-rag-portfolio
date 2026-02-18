import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MessageBubble } from '@/components/chat/MessageBubble'
import type { Message } from '@/types/models'

const mockUserMessage: Message = {
  id: '1',
  conversation_id: 'conv-1',
  role: 'user',
  content: 'Hello, world!',
  token_count: null,
  latency_ms: null,
  model: null,
  sources: [],
  feedback: null,
  created_at: '2024-01-01T00:00:00Z',
}

const mockAssistantMessage: Message = {
  id: '2',
  conversation_id: 'conv-1',
  role: 'assistant',
  content: 'Hi there! How can I help?',
  token_count: 10,
  latency_ms: 500,
  model: 'gpt-4o',
  sources: [
    {
      document_id: 'doc-1',
      chunk_index: 0,
      content_preview: 'This is a preview of the source content',
      similarity: 0.85,
    },
  ],
  feedback: null,
  created_at: '2024-01-01T00:00:01Z',
}

describe('MessageBubble', () => {
  it('renders user message content', () => {
    render(<MessageBubble message={mockUserMessage} />)
    expect(screen.getByText('Hello, world!')).toBeDefined()
  })

  it('renders assistant message content', () => {
    render(<MessageBubble message={mockAssistantMessage} />)
    expect(screen.getByText('Hi there! How can I help?')).toBeDefined()
  })

  it('displays sources for assistant messages', () => {
    render(<MessageBubble message={mockAssistantMessage} />)
    expect(screen.getByText('Sources:')).toBeDefined()
  })

  it('does not display sources section for user messages', () => {
    render(<MessageBubble message={mockUserMessage} />)
    expect(screen.queryByText('Sources:')).toBeNull()
  })
})
