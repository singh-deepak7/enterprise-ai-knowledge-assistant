import Container from "./Container";

export default function Footer() {
  return (
    <footer className="border-t border-border py-8">
      <Container>
        <p className="text-center text-sm text-muted-foreground">
          © 2026 Enterprise AI Knowledge Assistant.
          Built with Next.js, FastAPI, LangGraph and ChromaDB.
        </p>
      </Container>
    </footer>
  );
}