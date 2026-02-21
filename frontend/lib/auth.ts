const ACCESS_KEY = "rag_access_token";

export function setAccessToken(token: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem(ACCESS_KEY, token);
  }
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return localStorage.getItem(ACCESS_KEY);
}

export function clearAccessToken() {
  if (typeof window !== "undefined") {
    localStorage.removeItem(ACCESS_KEY);
  }
}
