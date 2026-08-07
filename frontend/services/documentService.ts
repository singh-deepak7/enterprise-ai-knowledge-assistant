import type { DocumentListResponse } from "@/types/document";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export async function getDocuments(): Promise<DocumentListResponse> {
  const response = await fetch(`${API_BASE_URL}/documents`, {
    method: "GET",
    cache: "no-store",
  });

  if (!response.ok) {
    let message = "Failed to load documents.";

    try {
      const error = (await response.json()) as {
        detail?: string;
        message?: string;
      };

      message = error.detail ?? error.message ?? message;
    } catch {
      // Keep the default message when the
      // backend response is not JSON.
    }

    throw new Error(message);
  }

  return (await response.json()) as DocumentListResponse;
}

export async function deleteDocument(documentId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    let message = "Failed to delete document.";

    try {
      const error = (await response.json()) as {
        detail?: string;
        message?: string;
      };

      message = error.detail ?? error.message ?? message;
    } catch {
      // Keep the default message when the
      // backend response is not JSON.
    }

    throw new Error(message);
  }
}
