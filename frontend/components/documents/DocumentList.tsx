import type { DocumentSummary } from "@/types/document";

interface DocumentListProps {
  documents: DocumentSummary[];
  deletingDocumentId: string | null;
  onDelete: (document: DocumentSummary) => void;
}

function formatFileSize(sizeBytes: number): string {
  if (sizeBytes < 1024) {
    return `${sizeBytes} B`;
  }

  const sizeKb = sizeBytes / 1024;

  if (sizeKb < 1024) {
    return `${sizeKb.toFixed(1)} KB`;
  }

  const sizeMb = sizeKb / 1024;

  return `${sizeMb.toFixed(1)} MB`;
}

function getFileType(contentType: string): string {
  switch (contentType) {
    case "application/pdf":
      return "PDF";

    case "text/plain":
      return "TXT";

    case "text/csv":
      return "CSV";

    case "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
      return "XLSX";

    default:
      return "Document";
  }
}

function formatUploadedAt(uploadedAt: string): string {
  if (!uploadedAt) {
    return "Unknown upload time";
  }

  const date = new Date(uploadedAt);

  if (Number.isNaN(date.getTime())) {
    return "Unknown upload time";
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export default function DocumentList({
  documents,
  deletingDocumentId,
  onDelete,
}: DocumentListProps) {
  if (documents.length === 0) {
    return (
      <div className="rounded-lg border border-dashed p-8 text-center">
        <p className="font-medium">No documents uploaded</p>

        <p className="mt-1 text-sm text-muted-foreground">
          Upload a document from the chat page to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {documents.map((document) => {
        const isDeleting = deletingDocumentId === document.document_id;

        return (
          <div
            key={document.document_id}
            className="flex items-center gap-4 rounded-lg border p-4"
          >
            <div className="text-2xl">📄</div>

            <div className="min-w-0 flex-1">
              <p className="truncate font-medium">
                {document.original_filename}
              </p>

              <p className="mt-1 text-sm text-muted-foreground">
                {getFileType(document.content_type)}
                {" • "}
                {formatFileSize(document.size_bytes)}
                {" • "}
                {document.chunk_count}{" "}
                {document.chunk_count === 1 ? "chunk" : "chunks"}
              </p>

              <p className="mt-1 text-xs text-muted-foreground">
                Uploaded {formatUploadedAt(document.uploaded_at)}
              </p>
            </div>

            <span className="rounded-full border px-2.5 py-1 text-xs font-medium capitalize">
              {document.status}
            </span>

            <button
              type="button"
              disabled={deletingDocumentId !== null}
              onClick={() => onDelete(document)}
              className="rounded-md border px-3 py-2 text-sm font-medium text-destructive transition-colors hover:bg-destructive/10 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isDeleting ? "Deleting..." : "Delete"}
            </button>
          </div>
        );
      })}
    </div>
  );
}
