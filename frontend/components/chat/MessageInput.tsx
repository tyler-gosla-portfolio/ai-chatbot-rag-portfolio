"use client";

import { FormEvent, useState } from "react";

export function MessageInput({ onSend, disabled = false }: { onSend: (text: string) => Promise<void>; disabled?: boolean }) {
  const [value, setValue] = useState("");

  async function submit(e: FormEvent) {
    e.preventDefault();
    const content = value.trim();
    if (!content) return;
    setValue("");
    await onSend(content);
  }

  return (
    <form onSubmit={submit} className="flex gap-2 mt-4">
      <input
        className="flex-1 border rounded px-3 py-2"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Ask a question about your documents"
      />
      <button className="px-4 py-2 rounded bg-slate-900 text-white" type="submit" disabled={disabled}>
        Send
      </button>
    </form>
  );
}
