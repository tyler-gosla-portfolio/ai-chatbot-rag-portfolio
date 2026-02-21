import { clearAccessToken, getAccessToken, setAccessToken } from "./auth";
import type { AuthResponse, Chat, ChatDetail, Document, Message } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", headers.get("Content-Type") ?? "application/json");

  const token = getAccessToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
    credentials: "include",
  });

  if (res.status === 401 && path !== "/auth/refresh") {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      return request<T>(path, init);
    }
  }

  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || `Request failed with ${res.status}`);
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return (await res.json()) as T;
}

export async function register(email: string, password: string): Promise<AuthResponse> {
  const data = await request<AuthResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setAccessToken(data.tokens.access_token);
  return data;
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  const data = await request<AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setAccessToken(data.tokens.access_token);
  return data;
}

export async function refreshAccessToken(): Promise<boolean> {
  try {
    const data = await request<{ access_token: string }>("/auth/refresh", { method: "POST" });
    setAccessToken(data.access_token);
    return true;
  } catch {
    clearAccessToken();
    return false;
  }
}

export async function logout() {
  await request<void>("/auth/logout", { method: "POST" });
  clearAccessToken();
}

export async function listDocuments(): Promise<Document[]> {
  return request<Document[]>("/documents");
}

export async function uploadDocument(file: File): Promise<Document> {
  const token = getAccessToken();
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE}/documents`, {
    method: "POST",
    body: form,
    credentials: "include",
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return (await res.json()) as Document;
}

export async function deleteDocument(id: string) {
  await request<void>(`/documents/${id}`, { method: "DELETE" });
}

export async function listChats(): Promise<Chat[]> {
  return request<Chat[]>("/chats");
}

export async function createChat(title: string, document_ids: string[] = []): Promise<Chat> {
  return request<Chat>("/chats", {
    method: "POST",
    body: JSON.stringify({ title, document_ids }),
  });
}

export async function getChat(id: string): Promise<ChatDetail> {
  return request<ChatDetail>(`/chats/${id}`);
}

export async function createMessage(chatId: string, content: string): Promise<Message> {
  return request<Message>(`/chats/${chatId}/messages`, {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}
