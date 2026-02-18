'use client'

import { ChatPanel } from '@/components/chat/ChatPanel'

export default function ConversationPage({ params }: { params: { id: string } }) {
  return <ChatPanel conversationId={params.id} />
}
