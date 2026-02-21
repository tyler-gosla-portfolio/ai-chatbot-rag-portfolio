"use client";

export function StreamingMessage({ text, active }: { text: string; active: boolean }) {
  if (!active && !text) {
    return null;
  }
  return (
    <div className="mt-3 p-3 rounded-lg border bg-cyan-50">
      <p className="text-xs uppercase text-slate-500">Streaming</p>
      <p>{text || "..."}</p>
    </div>
  );
}
