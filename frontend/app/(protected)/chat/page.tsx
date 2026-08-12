import ChatContainer from "@/components/chat/ChatContainer";
import DocumentUpload from "@/components/documents/DocumentUpload";

export default function ChatPage() {
  return (
    <main className="container mx-auto min-h-screen p-6">
      <div className="grid gap-6 lg:grid-cols-[320px_minmax(0,1fr)]">
        <aside>
          <DocumentUpload />
        </aside>

        <ChatContainer />
      </div>
    </main>
  );
}