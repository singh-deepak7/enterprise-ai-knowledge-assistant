"use client";

import { useEffect, useRef } from "react";

import type { ChatMessage as ChatMessageType } from "@/types/message";
import ChatMessage from "./ChatMessage";

interface ChatMessagesProps {
  messages: ChatMessageType[];
}

export default function ChatMessages({
  messages,
}: ChatMessagesProps) {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex h-full items-center justify-center rounded-lg border border-dashed p-10 text-center text-muted-foreground">
        <div>
          <h2 className="mb-2 text-lg font-semibold">
            Enterprise AI Assistant
          </h2>

          <p>
            Ask a question to begin a conversation.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      className="
        flex
        flex-col
        gap-4
        overflow-y-auto
        rounded-lg
        border
        p-4
      "
    >
      {messages.map((message) => (
        <ChatMessage
          key={message.id}
          message={message}
        />
      ))}

      <div ref={bottomRef} />
    </div>
  );
}