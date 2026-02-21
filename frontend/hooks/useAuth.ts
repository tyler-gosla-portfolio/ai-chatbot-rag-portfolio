"use client";

import { useState } from "react";
import { login, logout, register } from "../lib/api";

export function useAuth() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function signIn(email: string, password: string) {
    setLoading(true);
    setError(null);
    try {
      return await login(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
      throw err;
    } finally {
      setLoading(false);
    }
  }

  async function signUp(email: string, password: string) {
    setLoading(true);
    setError(null);
    try {
      return await register(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
      throw err;
    } finally {
      setLoading(false);
    }
  }

  async function signOut() {
    await logout();
  }

  return { signIn, signUp, signOut, loading, error };
}
