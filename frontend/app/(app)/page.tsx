"use client";

import Link from "next/link";
import { useChats } from "../../hooks/useChat";

export default function DashboardPage() {
  const { data, createChat, isLoading } = useChats();

  return (
    <section className="space-y-4">
      <div className="flex justify-between">
        <h1 className="text-2xl font-semibold">Chats</h1>
        <button
          className="bg-slate-900 text-white px-3 py-2 rounded"
          onClick={async () => {
            const chat = await createChat({ title: "New Chat", documentIds: [] });
            window.location.href = `/chat/${chat.id}`;
          }}
        >
          New chat
        </button>
      </div>

      {isLoading && <p>Loading chats...</p>}
      <ul className="space-y-2">
        {(data ?? []).map((chat) => (
          <li key={chat.id} className="bg-white border rounded p-3">
            <Link href={`/chat/${chat.id}`} className="font-semibold text-blue-700">
              {chat.title}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
