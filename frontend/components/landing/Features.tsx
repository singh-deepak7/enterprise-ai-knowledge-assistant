import {
  Bot,
  Database,
  FileSearch,
  ShieldCheck,
} from "lucide-react";

import Container from "@/components/layout/Container";

const features = [
  {
    title: "Agentic AI",
    description:
      "Planner, Retrieval, Reasoning and Validation agents working together.",
    icon: Bot,
  },
  {
    title: "Retrieval-Augmented Generation",
    description:
      "Ground responses using enterprise documents with semantic search.",
    icon: FileSearch,
  },
  {
    title: "ChromaDB Vector Store",
    description:
      "Persistent vector database with metadata and similarity search.",
    icon: Database,
  },
  {
    title: "Secure & Reliable",
    description:
      "Source citations, validation and guardrails reduce hallucinations.",
    icon: ShieldCheck,
  },
];

export default function Features() {
  return (
    <section id="features" className="py-20">
      <Container>
        <div className="mb-12 text-center">
          <h2 className="text-4xl font-bold">
            Built for Enterprise AI
          </h2>

          <p className="mt-4 text-muted-foreground">
            Production-ready architecture using modern AI technologies.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2 xl:grid-cols-4">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="rounded-2xl border bg-card p-8 transition hover:-translate-y-1 hover:shadow-lg"
            >
              <feature.icon className="mb-6 h-10 w-10 text-cyan-400" />

              <h3 className="mb-3 text-xl font-semibold">
                {feature.title}
              </h3>

              <p className="text-muted-foreground">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </Container>
    </section>
  );
}