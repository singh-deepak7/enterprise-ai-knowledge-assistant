import {
  FileUp,
  Scissors,
  Brain,
  Database,
  Search,
  Bot,
  ShieldCheck,
} from "lucide-react";

import Container from "@/components/layout/Container";
import SectionHeading from "@/components/common/SectionHeading";

const steps = [
  { title: "Upload Documents", icon: FileUp },
  { title: "Chunk Content", icon: Scissors },
  { title: "Generate Embeddings", icon: Brain },
  { title: "Store in ChromaDB", icon: Database },
  { title: "Semantic Retrieval", icon: Search },
  { title: "LangGraph Agents", icon: Bot },
  { title: "Validated Response", icon: ShieldCheck },
];

export default function Architecture() {
  return (
    <section id="architecture" className="py-24">
      <Container>
        <SectionHeading
          title="How It Works"
          description="An end-to-end Agentic AI + RAG pipeline."
        />

        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          {steps.map((step, index) => (
            <div
              key={step.title}
              className="rounded-2xl border bg-card/70 p-6 text-center"
            >
              <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-cyan-500/10">
                <step.icon className="h-7 w-7 text-cyan-400" />
              </div>

              <div className="mb-2 text-xs font-bold text-cyan-400">
                STEP {index + 1}
              </div>

              <h3 className="font-semibold">{step.title}</h3>
            </div>
          ))}
        </div>
      </Container>
    </section>
  );
}