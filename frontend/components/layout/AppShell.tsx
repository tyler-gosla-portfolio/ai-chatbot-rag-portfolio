"use client";

import Link from "next/link";
import { ReactNode } from "react";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen grid grid-cols-1 md:grid-cols-[220px_1fr]">
      <aside className="bg-slate-900 text-slate-100 p-6">
        <h2 className="text-xl font-semibold mb-4">RAG Assistant</h2>
        <nav className="space-y-2">
          <Link className="block hover:text-cyan-300" href="/">Dashboard</Link>
          <Link className="block hover:text-cyan-300" href="/documents">Documents</Link>
        </nav>
      </aside>
      <main className="p-6">{children}</main>
    </div>
  );
}
