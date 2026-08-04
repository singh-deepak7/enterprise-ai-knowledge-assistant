import Link from "next/link";
import { ArrowRight, Upload, Bot } from "lucide-react";

import Container from "@/components/layout/Container";

export default function Hero() {
  return (
    <section className="relative overflow-hidden py-24 sm:py-32">
      <Container>
        <div className="mx-auto max-w-4xl text-center">

          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 py-2 text-sm text-cyan-400">
            <Bot className="h-4 w-4" />
            Agentic AI • RAG • LangGraph • ChromaDB
          </div>

          <h1 className="text-5xl font-bold tracking-tight sm:text-7xl">
            Enterprise AI
            <span className="block bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              Knowledge Assistant
            </span>
          </h1>

          <p className="mx-auto mt-8 max-w-3xl text-lg text-muted-foreground">
            Upload enterprise documents and ask natural language questions.
            Powered by Agentic AI, Retrieval-Augmented Generation (RAG),
            LangGraph, and OpenAI.
          </p>

          <div className="mt-12 flex flex-col items-center justify-center gap-4 sm:flex-row">

            <Link
              href="/documents"
              className="inline-flex items-center gap-2 rounded-xl bg-cyan-500 px-6 py-3 font-semibold text-black transition hover:bg-cyan-400"
            >
              <Upload className="h-5 w-5" />
              Upload Documents
            </Link>

            <Link
              href="/chat"
              className="inline-flex items-center gap-2 rounded-xl border border-border px-6 py-3 font-semibold transition hover:bg-accent"
            >
              Start Chat
              <ArrowRight className="h-5 w-5" />
            </Link>

          </div>

        </div>
      </Container>
    </section>
  );
}