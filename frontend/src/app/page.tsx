import Link from 'next/link'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="max-w-2xl text-center">
        <h1 className="text-4xl font-bold mb-4">AI Chatbot with RAG</h1>
        <p className="text-lg text-gray-600 mb-8">
          Upload documents and chat with an AI that uses your content as context.
          Powered by RAG (Retrieval-Augmented Generation).
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/login"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
          >
            Create Account
          </Link>
        </div>
      </div>
    </main>
  )
}
