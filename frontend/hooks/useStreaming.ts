"use client";

import { useEffect, useRef, useState } from "react";
import { getAccessToken } from "../lib/auth";

export function useStreaming(chatId: string) {
  const wsRef = useRef<WebSocket | null>(null);
  const [streamText, setStreamText] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);

  useEffect(() => {
    return () => {
      wsRef.current?.close();
    };
  }, []);

  function connect() {
    const base = process.env.NEXT_PUBLIC_WS_BASE_URL ?? "ws://localhost:8000/api/v1";
    const token = getAccessToken();
    const socket = new WebSocket(`${base}/chats/${chatId}/messages/stream?token=${encodeURIComponent(token ?? "")}`);

    socket.addEventListener("message", (event) => {
      const data = JSON.parse(event.data);
      if (data.delta) {
        setStreamText((prev) => prev + data.delta);
      }
      if (data.done) {
        setIsStreaming(false);
      }
    });

    wsRef.current = socket;
    return socket;
  }

  function start(content: string) {
    setStreamText("");
    setIsStreaming(true);
    const socket = wsRef.current ?? connect();

    socket.onopen = () => {
      socket.send(JSON.stringify({ content }));
    };
    if (socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ content }));
    }
  }

  return { streamText, isStreaming, startStreaming: start };
}
