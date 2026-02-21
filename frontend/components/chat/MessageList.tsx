"use client";

import type { Message } from "../../lib/types";

export function MessageList({ messages }: { messages: Message[] }) {
  return (
    <div className="space-y-3">
      {messages.map((msg) => (
        <article
          key={msg.id}
          className={`p-3 rounded-lg ${msg.role === "user" ? "bg-blue-600 text-white" : "bg-white border"}`}
        >
          <p className="text-xs uppercase tracking-wide opacity-70 mb-1">{msg.role}</p>
          <p>{msg.content}</p>
        </article>
      ))}
    </div>
  );
}
