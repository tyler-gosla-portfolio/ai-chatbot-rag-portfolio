import type { Message } from '@/types/models'

interface MessageBubbleProps {
  message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-900'
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        {message.sources.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-200">
            <p className="text-xs text-gray-500 mb-1">Sources:</p>
            {message.sources.map((source, i) => (
              <p key={i} className="text-xs text-gray-400">
                [{source.chunk_index}] {source.content_preview.slice(0, 100)}...
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
