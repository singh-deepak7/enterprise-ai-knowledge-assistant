import Link from "next/link";

import Container from "@/components/layout/Container";

export default function CTA() {
  return (
    <section className="py-24">
      <Container>
        <div className="rounded-3xl border bg-card p-12 text-center">

          <h2 className="text-4xl font-bold">
            Ready to build your enterprise knowledge base?
          </h2>

          <p className="mx-auto mt-6 max-w-2xl text-muted-foreground">
            Upload documents, create embeddings, and chat with your enterprise
            knowledge using Agentic AI.
          </p>

          <Link
            href="/documents"
            className="mt-10 inline-flex rounded-xl bg-cyan-500 px-8 py-4 font-semibold text-black transition hover:bg-cyan-400"
          >
            Get Started
          </Link>

        </div>
      </Container>
    </section>
  );
}