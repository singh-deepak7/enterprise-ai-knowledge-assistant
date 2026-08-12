import {
  Brain,
  Database,
  Cloud,
  Boxes,
  Cpu,
  FileText,
  Code2,
  Server,
} from "lucide-react";

import Container from "@/components/layout/Container";
import SectionHeading from "@/components/common/SectionHeading";

const technologies = [
  {
    name: "Next.js",
    description: "Modern React Framework",
    icon: Code2,
  },
  {
    name: "FastAPI",
    description: "Backend REST API",
    icon: Server,
  },
  {
    name: "OpenAI GPT",
    description: "LLM Responses",
    icon: Brain,
  },
  {
    name: "LangGraph",
    description: "Agent Orchestration",
    icon: Boxes,
  },
  {
    name: "ChromaDB",
    description: "Vector Database",
    icon: Database,
  },
  {
    name: "AWS",
    description: "Cloud Deployment",
    icon: Cloud,
  },
  {
    name: "RAG",
    description: "Grounded Retrieval",
    icon: FileText,
  },
  {
    name: "Embeddings",
    description: "Semantic Search",
    icon: Cpu,
  },
];

export default function TechStack() {
  return (
    <section className="py-24">
      <Container>
        <SectionHeading
          title="Technology Stack"
          description="Built using modern cloud-native and Generative AI technologies."
        />

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {technologies.map((tech) => (
            <div
              key={tech.name}
              className="rounded-2xl border bg-card/70 p-6 backdrop-blur transition duration-300 hover:-translate-y-1 hover:border-cyan-400 hover:shadow-xl"
            >
              <tech.icon className="mb-4 h-10 w-10 text-cyan-400" />

              <h3 className="text-lg font-semibold">{tech.name}</h3>

              <p className="mt-2 text-sm text-muted-foreground">
                {tech.description}
              </p>
            </div>
          ))}
        </div>
      </Container>
    </section>
  );
}