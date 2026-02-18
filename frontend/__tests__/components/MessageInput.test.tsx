import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MessageInput } from '@/components/chat/MessageInput'

describe('MessageInput', () => {
  it('renders input field and send button', () => {
    render(<MessageInput onSend={() => {}} />)
    expect(screen.getByPlaceholderText('Type a message...')).toBeDefined()
    expect(screen.getByText('Send')).toBeDefined()
  })

  it('calls onSend with input value on submit', () => {
    const onSend = vi.fn()
    render(<MessageInput onSend={onSend} />)

    const input = screen.getByPlaceholderText('Type a message...')
    fireEvent.change(input, { target: { value: 'Test message' } })
    fireEvent.submit(input.closest('form')!)

    expect(onSend).toHaveBeenCalledWith('Test message')
  })

  it('clears input after sending', () => {
    render(<MessageInput onSend={() => {}} />)

    const input = screen.getByPlaceholderText('Type a message...') as HTMLInputElement
    fireEvent.change(input, { target: { value: 'Test message' } })
    fireEvent.submit(input.closest('form')!)

    expect(input.value).toBe('')
  })

  it('does not send empty messages', () => {
    const onSend = vi.fn()
    render(<MessageInput onSend={onSend} />)

    const form = screen.getByPlaceholderText('Type a message...').closest('form')!
    fireEvent.submit(form)

    expect(onSend).not.toHaveBeenCalled()
  })

  it('disables input when disabled prop is true', () => {
    render(<MessageInput onSend={() => {}} disabled />)

    const input = screen.getByPlaceholderText('Type a message...')
    expect(input).toHaveProperty('disabled', true)
  })
})
