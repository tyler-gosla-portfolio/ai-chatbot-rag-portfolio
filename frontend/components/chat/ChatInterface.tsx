"use client";

import { useChat } from "../../hooks/useChat";
import { useStreaming } from "../../hooks/useStreaming";
import { MessageInput } from "./MessageInput";
import { MessageList } from "./MessageList";
import { StreamingMessage } from "./StreamingMessage";

export function ChatInterface({ chatId }: { chatId: string }) {
  const { data, isLoading, sendMessage, sending } = useChat(chatId);
  const { streamText, isStreaming, startStreaming } = useStreaming(chatId);

  async function onSend(content: string) {
    await sendMessage(content);
    startStreaming(content);
  }

  if (isLoading) {
    return <p>Loading chat...</p>;
  }

  return (
    <section>
      <MessageList messages={data?.messages ?? []} />
      <StreamingMessage text={streamText} active={isStreaming} />
      <MessageInput onSend={onSend} disabled={sending || isStreaming} />
    </section>
  );
}
