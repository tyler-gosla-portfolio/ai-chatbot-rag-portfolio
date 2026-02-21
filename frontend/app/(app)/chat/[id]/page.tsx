import { ChatInterface } from "../../../../components/chat/ChatInterface";

export default function ChatPage({ params }: { params: { id: string } }) {
  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">Chat</h1>
      <ChatInterface chatId={params.id} />
    </section>
  );
}
