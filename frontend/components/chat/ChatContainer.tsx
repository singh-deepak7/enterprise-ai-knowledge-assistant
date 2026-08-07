"use client";

import { useState } from "react";

import { chatService } from "@/services/chatService";
import type { ChatResponse } from "@/types/chat";

export default function ChatContainer() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit() {
    if (!question.trim()) {
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const result = await chatService.ask({
        question,
      });

      setResponse(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-6 rounded-lg border p-6">
      <div>
        <h1 className="text-2xl font-semibold">
          Enterprise AI Assistant
        </h1>

        <p className="text-muted-foreground">
          Ask questions about your knowledge base.
        </p>
      </div>

      <div className="space-y-3">
        <textarea
          className="min-h-32 w-full rounded-md border p-3"
          placeholder="Ask your question..."
          value={question}
          onChange={(event) =>
            setQuestion(event.target.value)
          }
        />

        <button
          className="rounded-md bg-primary px-4 py-2 text-primary-foreground"
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? "Thinking..." : "Ask"}
        </button>
      </div>

      {error && (
        <div className="rounded-md border border-red-500 p-3 text-red-500">
          {error}
        </div>
      )}

      {response && (
        <div className="space-y-3 rounded-md bg-muted p-4">
          <h2 className="font-semibold">
            Answer
          </h2>

          <p>
            {response.answer}
          </p>

          <p className="text-sm text-muted-foreground">
            Sources: {response.sources.length}
          </p>
        </div>
      )}
    </section>
  );
}