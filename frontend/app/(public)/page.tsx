export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <section className="mx-auto flex min-h-screen max-w-7xl flex-col items-center justify-center px-6 text-center">

        <div className="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 py-1 text-sm text-cyan-300">
          Agentic AI • RAG • LangGraph • ChromaDB
        </div>

        <h1 className="mt-8 text-6xl font-bold tracking-tight">
          Enterprise AI
          <span className="block text-cyan-400">
            Knowledge Assistant
          </span>
        </h1>

        <p className="mt-8 max-w-3xl text-lg text-slate-300">
          Upload enterprise documents and ask natural language
          questions using Agentic AI, Retrieval-Augmented Generation,
          and Large Language Models.
        </p>

        <div className="mt-10 flex gap-5">

          <button className="rounded-lg bg-cyan-500 px-6 py-3 font-semibold text-black transition hover:bg-cyan-400">
            Upload Documents
          </button>

          <button className="rounded-lg border border-slate-600 px-6 py-3 transition hover:bg-slate-800">
            Open Chat
          </button>

        </div>

      </section>
    </main>
  );
}