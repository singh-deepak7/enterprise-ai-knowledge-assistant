"use client";

import { useState } from "react";

import { streamChat } from "@/services/chatStreamService";

import type { ChatSource } from "@/types/chat";

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

function getDisplayFileName(path: string): string {
  return path.split("/").pop() ?? path;
}

export default function ChatContainer() {
  const [question, setQuestion] = useState("");

  const [answer, setAnswer] = useState("");

  const [confidenceScore, setConfidenceScore] = useState<number | null>(null);

  const [events, setEvents] = useState<string[]>([]);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState<string | null>(null);

  const [sources, setSources] = useState<ChatSource[]>([]);

  async function handleSubmit() {
    if (!question.trim()) {
      return;
    }

    setLoading(true);
    setError(null);
    setAnswer("");
    setConfidenceScore(null);
    setSources([]);
    setEvents([]);

    try {
      await streamChat(
        {
          question,
        },

        (event) => {
          const status = getWorkflowStatus(event);

          if (status) {
            setEvents((previous) => [...previous, status]);
          }

          if (typeof event === "object" && event !== null) {
            const value = Object.values(event)[0];

            if (typeof value === "object" && value !== null) {
              if ("answer" in value && typeof value.answer === "string") {
                setAnswer(value.answer);
              }

              if (
                "confidence_score" in value &&
                typeof value.confidence_score === "number"
              ) {
                setConfidenceScore(value.confidence_score);
              }

              if ("sources" in value && Array.isArray(value.sources)) {
                setSources(value.sources);
              }
            }
          }
        },
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Streaming failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section
      className="
        space-y-6
        rounded-lg
        border
        p-6
      "
    >
      <div>
        <h1 className="text-2xl font-semibold">Enterprise AI Assistant</h1>

        <p className="text-muted-foreground">
          Ask questions about your knowledge base.
        </p>
      </div>

      <textarea
        className="
          min-h-32
          w-full
          rounded-md
          border
          p-3
        "
        placeholder="Ask your question..."
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
      />

      <button
        className="
          rounded-md
          bg-primary
          px-4
          py-2
          text-primary-foreground
        "
        disabled={loading}
        onClick={handleSubmit}
      >
        {loading ? "Generating..." : "Ask"}
      </button>

      {error && (
        <div
          className="
            rounded-md
            border
            border-red-500
            p-3
            text-red-500
          "
        >
          {error}
        </div>
      )}

      {events.length > 0 && (
        <div
          className="
            rounded-md
            bg-muted
            p-4
            text-sm
          "
        >
          <h2 className="mb-2 font-semibold">Workflow Status</h2>

          {events.map((event, index) => (
            <div key={index}>{event}</div>
          ))}
        </div>
      )}

      {confidenceScore !== null && (
        <div
          className="
      rounded-md
      border
      p-3
      text-sm
    "
        >
          Confidence Score: {(confidenceScore * 100).toFixed(0)}%
        </div>
      )}

      {answer && (
        <div
          className="
            rounded-md
            bg-muted
            p-4
          "
        >
          <h2 className="font-semibold">Answer</h2>

          <p className="mt-2">{answer}</p>
        </div>
      )}

      {sources.length > 0 && (
        <div
          className="
      rounded-md
      border
      p-4
    "
        >
          <h2 className="font-semibold">📚 Sources</h2>

          <div className="mt-3 space-y-2">
            {sources.map((source, index) => (
              <div key={index} className="text-sm">
                📄 {getDisplayFileName(source.source)}
                <div>Page {source.page}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
