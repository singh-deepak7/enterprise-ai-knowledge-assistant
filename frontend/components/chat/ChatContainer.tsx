"use client";

import { useState } from "react";

import {
  streamChat,
  type ChatStreamEvent,
} from "@/services/chatStreamService";
import type { ChatMessage } from "@/types/message";

import ChatMessages from "./ChatMessages";

function getWorkflowStatus(
  event: ChatStreamEvent,
): string | null {
  if (event.type !== "updates") {
    return null;
  }

  const node = Object.keys(event.data)[0];

  switch (node) {
    case "planner":
      return "🧭 Planning request...";

    case "retrieval":
      return "🔎 Searching knowledge base...";

    case "reasoning":
      return "🧠 Generating answer...";

    case "validation":
      return "✅ Validating sources...";

    default:
      return null;
  }
}

function getWorkflowValue(
  event: ChatStreamEvent,
): Record<string, unknown> | null {
  if (event.type !== "updates") {
    return null;
  }

  const value = Object.values(event.data)[0];

  if (
    typeof value !== "object" ||
    value === null
  ) {
    return null;
  }

  return value as Record<string, unknown>;
}

export default function ChatContainer() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit() {
    const submittedQuestion = question.trim();

    if (!submittedQuestion || loading) {
      return;
    }

    const userMessageId = crypto.randomUUID();
    const assistantMessageId = crypto.randomUUID();

    const userMessage: ChatMessage = {
      id: userMessageId,
      role: "user",
      content: submittedQuestion,
      createdAt: new Date(),
    };

    const assistantMessage: ChatMessage = {
      id: assistantMessageId,
      role: "assistant",
      content: "",
      status: "🧭 Planning request...",
      createdAt: new Date(),
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
      assistantMessage,
    ]);

    setQuestion("");
    setError(null);
    setLoading(true);

    try {
      await streamChat(
        {
          question: submittedQuestion,
        },
        (event) => {
          /*
           * LLM token/chunk event.
           */
          if (event.type === "token") {
            const content = event.data.content;

            if (!content) {
              return;
            }

            setMessages((previous) =>
              previous.map((message) =>
                message.id === assistantMessageId
                  ? {
                      ...message,
                      content:
                        message.content + content,
                      status: undefined,
                    }
                  : message,
              ),
            );

            return;
          }

          /*
           * LangGraph node update.
           */
          const status = getWorkflowStatus(event);

          if (status) {
            setMessages((previous) =>
              previous.map((message) =>
                message.id === assistantMessageId
                  ? {
                      ...message,
                      status,
                    }
                  : message,
              ),
            );
          }

          const value = getWorkflowValue(event);

          if (!value) {
            return;
          }

          setMessages((previous) =>
            previous.map((message) => {
              if (message.id !== assistantMessageId) {
                return message;
              }

              const completeAnswer =
                typeof value.answer === "string"
                  ? value.answer
                  : "";

              const confidenceScore =
                typeof value.confidence_score === "number"
                  ? value.confidence_score
                  : message.confidenceScore;

              const sources = Array.isArray(value.sources)
                ? value.sources
                : message.sources;

              return {
                ...message,

                content:
                  message.content ||
                  completeAnswer,

                confidenceScore,

                sources,
              };
            }),
          );
        },
      );
    } catch (err) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : "Streaming failed";

      setError(errorMessage);

      setMessages((previous) =>
        previous.map((message) =>
          message.id === assistantMessageId
            ? {
                ...message,
                content:
                  message.content ||
                  "Unable to generate a response. Please try again.",
                status: undefined,
              }
            : message,
        ),
      );
    } finally {
      setLoading(false);

      setMessages((previous) =>
        previous.map((message) =>
          message.id === assistantMessageId
            ? {
                ...message,
                status: undefined,
              }
            : message,
        ),
      );
    }
  }

  return (
    <section className="flex min-h-[70vh] flex-col rounded-lg border">
      <div className="border-b p-6">
        <h1 className="text-2xl font-semibold">
          Enterprise AI Assistant
        </h1>

        <p className="text-muted-foreground">
          Ask questions about your knowledge base.
        </p>
      </div>

      <div className="min-h-0 flex-1 p-6">
        <ChatMessages messages={messages} />
      </div>

      {error && (
        <div className="px-6 pb-4">
          <div className="rounded-md border border-red-500 p-3 text-sm text-red-500">
            {error}
          </div>
        </div>
      )}

      <div className="border-t p-6">
        <div className="flex gap-3">
          <textarea
            className="min-h-24 flex-1 resize-none rounded-md border p-3"
            placeholder="Ask your question..."
            value={question}
            disabled={loading}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
          />

          <button
            type="button"
            className="self-end rounded-md bg-primary px-5 py-3 text-primary-foreground disabled:cursor-not-allowed disabled:opacity-50"
            disabled={loading || !question.trim()}
            onClick={handleSubmit}
          >
            {loading ? "Generating..." : "Ask"}
          </button>
        </div>
      </div>
    </section>
  );
}