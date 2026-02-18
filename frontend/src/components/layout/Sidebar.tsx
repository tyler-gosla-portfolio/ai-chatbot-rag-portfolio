'use client'

import Link from 'next/link'

export function Sidebar() {
  return (
    <aside className="w-64 bg-gray-900 text-white flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-lg font-semibold">AI Chatbot</h2>
      </div>
      <nav className="flex-1 p-4 space-y-2">
        <Link
          href="/"
          className="block px-3 py-2 rounded hover:bg-gray-800 transition"
        >
          Conversations
        </Link>
        <Link
          href="/documents"
          className="block px-3 py-2 rounded hover:bg-gray-800 transition"
        >
          Documents
        </Link>
      </nav>
      <div className="p-4 border-t border-gray-700">
        <button className="text-sm text-gray-400 hover:text-white">
          Sign Out
        </button>
      </div>
    </aside>
  )
}
