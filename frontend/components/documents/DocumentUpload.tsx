"use client";

import { useState } from "react";

import { uploadDocument } from "@/services/uploadService";
import type { UploadResponse } from "@/types/upload";

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

export default function DocumentUpload() {
  const [selectedFile, setSelectedFile] =
    useState<File | null>(null);

  const [uploading, setUploading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const [result, setResult] =
    useState<UploadResponse | null>(null);

  function handleFileChange(
    event: React.ChangeEvent<HTMLInputElement>,
  ) {
    const file =
      event.target.files?.[0] ?? null;

    setSelectedFile(file);
    setError(null);
    setResult(null);
  }

  async function handleUpload() {
    if (!selectedFile || uploading) {
      return;
    }

    setUploading(true);
    setError(null);
    setResult(null);

    try {
      const response =
        await uploadDocument(
          selectedFile,
        );

      setResult(response);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Document upload failed.",
      );
    } finally {
      setUploading(false);
    }
  }

  return (
    <section className="space-y-4 rounded-lg border p-6">
      <div>
        <h2 className="text-lg font-semibold">
          Upload Document
        </h2>

        <p className="text-sm text-muted-foreground">
          Add a document to the enterprise knowledge base.
        </p>
      </div>

      <input
        type="file"
        disabled={uploading}
        onChange={handleFileChange}
        className="block w-full text-sm"
      />

      {selectedFile && (
        <div className="rounded-md bg-muted p-3 text-sm">
          <div className="font-medium">
            {selectedFile.name}
          </div>

          <div className="text-muted-foreground">
            {formatFileSize(
              selectedFile.size,
            )}
          </div>
        </div>
      )}

      <button
        type="button"
        onClick={handleUpload}
        disabled={
          !selectedFile ||
          uploading
        }
        className="rounded-md bg-primary px-4 py-2 text-primary-foreground disabled:cursor-not-allowed disabled:opacity-50"
      >
        {uploading
          ? "Uploading..."
          : "Upload"}
      </button>

      {error && (
        <div className="rounded-md border border-red-500 p-3 text-sm text-red-500">
          {error}
        </div>
      )}

      {result && (
        <div className="rounded-md border p-4 text-sm">
          <div className="font-medium">
            {result.message}
          </div>

          <div className="mt-2 text-muted-foreground">
            {result.data.original_filename}
          </div>

          <div className="text-muted-foreground">
            {formatFileSize(
              result.data.size_bytes,
            )}
          </div>
        </div>
      )}
    </section>
  );
}