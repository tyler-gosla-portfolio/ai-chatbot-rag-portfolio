"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createChat, createMessage, getChat, listChats } from "../lib/api";

export function useChats() {
  const qc = useQueryClient();

  const chatsQuery = useQuery({
    queryKey: ["chats"],
    queryFn: listChats,
  });

  const createChatMutation = useMutation({
    mutationFn: ({ title, documentIds }: { title: string; documentIds: string[] }) => createChat(title, documentIds),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["chats"] }),
  });

  return {
    ...chatsQuery,
    createChat: createChatMutation.mutateAsync,
  };
}

export function useChat(chatId: string) {
  const qc = useQueryClient();

  const chatQuery = useQuery({
    queryKey: ["chat", chatId],
    queryFn: () => getChat(chatId),
    enabled: !!chatId,
  });

  const messageMutation = useMutation({
    mutationFn: (content: string) => createMessage(chatId, content),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["chat", chatId] }),
  });

  return {
    ...chatQuery,
    sendMessage: messageMutation.mutateAsync,
    sending: messageMutation.isPending,
  };
}
