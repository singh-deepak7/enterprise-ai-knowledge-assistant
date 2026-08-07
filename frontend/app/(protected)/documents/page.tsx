"use client";

import { useEffect, useState } from "react";

import DocumentList from "@/components/documents/DocumentList";
import { deleteDocument, getDocuments } from "@/services/documentService";

import type { DocumentSummary } from "@/types/document";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingDocumentId, setDeletingDocumentId] = useState<string | null>(
    null,
  );

  useEffect(() => {
    async function loadDocuments() {
      try {
        setError(null);

        const response = await getDocuments();

        setDocuments(response.documents);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load documents.",
        );
      } finally {
        setLoading(false);
      }
    }

    void loadDocuments();
  }, []);

  async function handleDelete(document: DocumentSummary) {
    const confirmed = window.confirm(
      `Delete "${document.original_filename}"? This document will no longer be available to the knowledge assistant.`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setError(null);

      setDeletingDocumentId(document.document_id);

      await deleteDocument(document.document_id);

      setDocuments((current) =>
        current.filter((item) => item.document_id !== document.document_id),
      );
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to delete document.",
      );
    } finally {
      setDeletingDocumentId(null);
    }
  }

  return (
    <section className="mx-auto w-full max-w-5xl space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-semibold">Documents</h1>

        <p className="mt-1 text-muted-foreground">
          Documents available to the knowledge assistant.
        </p>
      </div>

      {loading && (
        <div className="rounded-lg border p-6 text-sm text-muted-foreground">
          Loading documents...
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-destructive p-4 text-sm text-destructive">
          {error}
        </div>
      )}

      {!loading && !error && (
        <DocumentList
          documents={documents}
          deletingDocumentId={deletingDocumentId}
          onDelete={handleDelete}
        />
      )}
    </section>
  );
}
