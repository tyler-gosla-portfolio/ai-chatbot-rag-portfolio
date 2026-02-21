export type AuthResponse = {
  user: { id: string; email: string };
  tokens: { access_token: string; token_type: string };
};

export type Document = {
  id: string;
  filename: string;
  file_size: number;
  content_type: string;
  status: string;
  chunk_count: number;
  total_tokens: number;
  created_at: string;
};

export type Message = {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  sources?: Array<Record<string, unknown>>;
  created_at: string;
};

export type Chat = {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
};

export type ChatDetail = Chat & {
  messages: Message[];
  document_ids: string[];
};
