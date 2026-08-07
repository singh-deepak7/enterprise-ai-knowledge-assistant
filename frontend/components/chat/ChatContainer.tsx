"use client";

import { useState } from "react";

import { streamChat } from "@/services/chatStreamService";

export default function ChatContainer() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [events, setEvents] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);


  async function handleSubmit() {
    if (!question.trim()) {
      return;
    }


    setLoading(true);
    setError(null);
    setAnswer("");
    setEvents([]);


    try {
      await streamChat(
        {
          question,
        },
        (event) => {
          const message =
            JSON.stringify(event);


          setEvents((previous) => [
            ...previous,
            message,
          ]);


          /*
           Later we will replace this
           with token extraction.
          */

          if (
            typeof event === "object" &&
            event !== null
          ) {
            const value =
              Object.values(event)[0];


            if (
              typeof value === "object" &&
              value !== null &&
              "answer" in value
            ) {
              setAnswer(
                String(
                  value.answer,
                ),
              );
            }
          }
        },
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Streaming failed",
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
        disabled={loading}
        onClick={handleSubmit}
      >
        {loading
          ? "Generating..."
          : "Ask"}
      </button>


      {error && (
        <div className="rounded-md border border-red-500 p-3 text-red-500">
          {error}
        </div>
      )}


      {events.length > 0 && (
        <div className="rounded-md bg-muted p-4 text-sm">

          <h2 className="mb-2 font-semibold">
            Workflow Events
          </h2>

          {events.map(
            (event, index) => (
              <div key={index}>
                {event}
              </div>
            ),
          )}

        </div>
      )}


      {answer && (
        <div className="rounded-md bg-muted p-4">

          <h2 className="font-semibold">
            Answer
          </h2>

          <p className="mt-2">
            {answer}
          </p>

        </div>
      )}

    </section>
  );
}