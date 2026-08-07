"use client";

import { useState } from "react";

import { streamChat } from "@/services/chatStreamService";
import type { ChatMessage } from "@/types/message";

import ChatMessages from "./ChatMessages";

function getWorkflowStatus(event: unknown): string | null {
  if (typeof event !== "object" || event === null) {
    return null;
  }

  const node = Object.keys(event)[0];

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

export default function ChatContainer() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [events, setEvents] = useState<string[]>([]);
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
      createdAt: new Date(),
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
      assistantMessage,
    ]);

    setQuestion("");
    setEvents([]);
    setError(null);
    setLoading(true);

    try {
      await streamChat(
        {
          question: submittedQuestion,
        },
        (event) => {
          const status = getWorkflowStatus(event);

          if (status) {
            setEvents((previous) => [
              ...previous,
              status,
            ]);

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

          if (
            typeof event !== "object" ||
            event === null
          ) {
            return;
          }

          const value = Object.values(event)[0];

          if (
            typeof value !== "object" ||
            value === null
          ) {
            return;
          }

          setMessages((previous) =>
            previous.map((message) => {
              if (message.id !== assistantMessageId) {
                return message;
              }

              return {
                ...message,

                content:
                  "answer" in value &&
                  typeof value.answer === "string" &&
                  value.answer.length > 0
                    ? value.answer
                    : message.content,

                confidenceScore:
                  "confidence_score" in value &&
                  typeof value.confidence_score === "number"
                    ? value.confidence_score
                    : message.confidenceScore,

                sources:
                  "sources" in value &&
                  Array.isArray(value.sources) &&
                  value.sources.length > 0
                    ? value.sources
                    : message.sources,
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

      {events.length > 0 && loading && (
        <div className="px-6 pb-4">
          <div className="rounded-md bg-muted p-3 text-sm">
            <div className="font-medium">
              Workflow Status
            </div>

            <div className="mt-1 text-muted-foreground">
              {events[events.length - 1]}
            </div>
          </div>
        </div>
      )}

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

      <pre>{JSON.stringify(messages, null, 2)}</pre>
    </section>
  );
}

      

