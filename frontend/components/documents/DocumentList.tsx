import type { DocumentSummary } from "@/types/document";

interface DocumentListProps {
  documents: DocumentSummary[];
}

function formatFileSize(
  sizeBytes: number,
): string {
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

function getFileType(
  contentType: string,
): string {
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

export default function DocumentList({
  documents,
}: DocumentListProps) {
  if (documents.length === 0) {
    return (
      <div className="rounded-lg border border-dashed p-8 text-center">
        <p className="font-medium">
          No documents uploaded
        </p>

        <p className="mt-1 text-sm text-muted-foreground">
          Upload a document from the chat page to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {documents.map((document) => (
        <div
          key={document.document_id}
          className="flex items-center gap-4 rounded-lg border p-4"
        >
          <div className="text-2xl">
            📄
          </div>

          <div className="min-w-0 flex-1">
            <p className="truncate font-medium">
              {document.original_filename}
            </p>

            <p className="mt-1 text-sm text-muted-foreground">
              {getFileType(
                document.content_type,
              )}
              {" • "}
              {formatFileSize(
                document.size_bytes,
              )}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}