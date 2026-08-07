import type { ChatRequest } from "@/types/chat";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://localhost:8000/api/v1";

export interface WorkflowUpdateEvent {
  type: "updates";
  data: Record<string, unknown>;
}

export interface TokenStreamEvent {
  type: "token";
  data: {
    content: string;
    node?: string;
  };
}

export type ChatStreamEvent =
  | WorkflowUpdateEvent
  | TokenStreamEvent;

export async function streamChat(
  request: ChatRequest,
  onMessage: (event: ChatStreamEvent) => void,
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/chat/stream`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    },
  );

  if (!response.ok) {
    throw new Error(
      `Streaming request failed: ${response.status}`,
    );
  }

  if (!response.body) {
    throw new Error(
      "Streaming response body missing",
    );
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();

    if (done) {
      break;
    }

    buffer += decoder.decode(value, {
      stream: true,
    });

    const events = buffer.split("\n\n");

    buffer = events.pop() ?? "";

    for (const event of events) {
      if (!event.startsWith("data:")) {
        continue;
      }

      const payload = event
        .replace("data:", "")
        .trim();

      if (!payload) {
        continue;
      }

      const parsed: unknown = JSON.parse(payload);

      if (!isChatStreamEvent(parsed)) {
        continue;
      }

      onMessage(parsed);
    }
  }
}

function isChatStreamEvent(
  value: unknown,
): value is ChatStreamEvent {
  if (
    typeof value !== "object" ||
    value === null ||
    !("type" in value) ||
    !("data" in value)
  ) {
    return false;
  }

  if (value.type === "updates") {
    return (
      typeof value.data === "object" &&
      value.data !== null
    );
  }

  if (value.type === "token") {
    if (
      typeof value.data !== "object" ||
      value.data === null ||
      !("content" in value.data)
    ) {
      return false;
    }

    return typeof value.data.content === "string";
  }

  return false;
}