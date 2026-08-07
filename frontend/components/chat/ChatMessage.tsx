"use client";

import type { ChatSource } from "@/types/chat";
import type { ChatMessage as ChatMessageType } from "@/types/message";

function getDisplayFileName(path: string): string {
  return path.split("/").pop() ?? path;
}

function deduplicateSources(
  sources: ChatSource[] | undefined,
): ChatSource[] {
  if (!sources) {
    return [];
  }

  const uniqueSources = new Map<string, ChatSource>();

  for (const source of sources) {
    const key = `${source.source}:${source.page}`;

    if (!uniqueSources.has(key)) {
      uniqueSources.set(key, source);
    }
  }

  return Array.from(uniqueSources.values());
}

interface ChatMessageProps {
  message: ChatMessageType;
}

export default function ChatMessage({
  message,
}: ChatMessageProps) {
  const isUser = message.role === "user";

  const showStatus =
    !isUser &&
    !message.content &&
    Boolean(message.status);

  const sources = deduplicateSources(
    message.sources,
  );

  return (
    <div
      className={`flex ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      <div
        className={`max-w-3xl rounded-lg border p-4 ${
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-muted"
        }`}
      >
        {showStatus ? (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span
              className="inline-block h-2 w-2 animate-pulse rounded-full bg-current"
              aria-hidden="true"
            />

            <span>{message.status}</span>
          </div>
        ) : (
          <div className="whitespace-pre-wrap">
            {message.content}
          </div>
        )}

        {!isUser &&
          message.confidenceScore !== undefined && (
            <div className="mt-3 text-sm opacity-80">
              Evidence Confidence:{" "}
              {(message.confidenceScore * 100).toFixed(0)}%
            </div>
          )}

        {!isUser && sources.length > 0 && (
          <div className="mt-4">
            <div className="mb-2 font-medium">
              Sources
            </div>

            <div className="space-y-2 text-sm">
              {sources.map((source) => (
                <div
                  key={`${source.source}:${source.page}`}
                >
                  📄{" "}
                  {getDisplayFileName(
                    source.source,
                  )}

                  <div>
                    Page {source.page}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}