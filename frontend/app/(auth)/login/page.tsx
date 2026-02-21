"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../../../hooks/useAuth";

export default function LoginPage() {
  const router = useRouter();
  const { signIn, loading, error } = useAuth();
  const [email, setEmail] = useState("test@example.com");
  const [password, setPassword] = useState("password123");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    await signIn(email, password);
    router.push("/");
  }

  return (
    <main className="min-h-screen grid place-items-center">
      <form className="bg-white p-8 rounded-lg border w-full max-w-md" onSubmit={onSubmit}>
        <h1 className="text-xl font-semibold mb-4">Login</h1>
        <input className="w-full border rounded px-3 py-2 mb-3" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input
          className="w-full border rounded px-3 py-2 mb-3"
          value={password}
          type="password"
          onChange={(e) => setPassword(e.target.value)}
        />
        {error && <p className="text-rose-600 text-sm mb-3">{error}</p>}
        <button className="w-full bg-slate-900 text-white px-4 py-2 rounded" disabled={loading}>
          Sign in
        </button>
      </form>
    </main>
  );
}
