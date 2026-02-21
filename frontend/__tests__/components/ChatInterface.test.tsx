import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("../../hooks/useChat", () => ({
  useChat: () => ({
    data: {
      messages: [
        { id: "1", role: "assistant", content: "hello", created_at: new Date().toISOString() },
      ],
    },
    isLoading: false,
    sendMessage: vi.fn(),
    sending: false,
  }),
}));

vi.mock("../../hooks/useStreaming", () => ({
  useStreaming: () => ({
    streamText: "",
    isStreaming: false,
    startStreaming: vi.fn(),
  }),
}));

import { ChatInterface } from "../../components/chat/ChatInterface";

describe("ChatInterface", () => {
  it("renders existing messages", () => {
    render(<ChatInterface chatId="chat-1" />);
    expect(screen.getByText("hello")).toBeInTheDocument();
  });
});
