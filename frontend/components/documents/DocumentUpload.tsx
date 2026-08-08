"use client";

import { useState } from "react";

import { uploadDocument } from "@/services/uploadService";
import type { UploadResponse } from "@/types/upload";

const MAX_UPLOAD_SIZE_MB = 25;
const MAX_UPLOAD_SIZE_BYTES =
  MAX_UPLOAD_SIZE_MB * 1024 * 1024;

const ALLOWED_EXTENSIONS = [
  ".pdf",
  ".txt",
  ".csv",
  ".xlsx",
];

const ACCEPTED_FILE_TYPES = [
  ".pdf",
  ".txt",
  ".csv",
  ".xlsx",
].join(",");

interface DocumentUploadProps {
  onUploadSuccess?: (
    response: UploadResponse,
  ) => void | Promise<void>;
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

function getFileExtension(
  filename: string,
): string {
  const lastDotIndex =
    filename.lastIndexOf(".");

  if (lastDotIndex === -1) {
    return "";
  }

  return filename
    .slice(lastDotIndex)
    .toLowerCase();
}

function validateFile(
  file: File,
): string | null {
  const extension =
    getFileExtension(file.name);

  if (
    !ALLOWED_EXTENSIONS.includes(
      extension,
    )
  ) {
    return (
      "Unsupported file type. " +
      "Allowed types: PDF, TXT, CSV, XLSX."
    );
  }

  if (file.size === 0) {
    return "The selected file is empty.";
  }

  if (
    file.size >
    MAX_UPLOAD_SIZE_BYTES
  ) {
    return (
      `File is too large. ` +
      `Maximum size is ${MAX_UPLOAD_SIZE_MB} MB.`
    );
  }

  return null;
}

export default function DocumentUpload({
  onUploadSuccess,
}: DocumentUploadProps) {
  const [
    selectedFile,
    setSelectedFile,
  ] = useState<File | null>(null);

  const [
    uploading,
    setUploading,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<string | null>(null);

  const [
    result,
    setResult,
  ] = useState<UploadResponse | null>(
    null,
  );

  function handleFileChange(
    event: React.ChangeEvent<HTMLInputElement>,
  ) {
    const file =
      event.target.files?.[0] ??
      null;

    setError(null);
    setResult(null);

    if (!file) {
      setSelectedFile(null);
      return;
    }

    const validationError =
      validateFile(file);

    if (validationError) {
      setSelectedFile(null);
      setError(validationError);

      event.target.value = "";

      return;
    }

    setSelectedFile(file);
  }

  async function handleUpload() {
    if (
      !selectedFile ||
      uploading
    ) {
      return;
    }

    const validationError =
      validateFile(selectedFile);

    if (validationError) {
      setError(validationError);
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

      if (onUploadSuccess) {
        await onUploadSuccess(
          response,
        );
      }
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
          Add a document to the enterprise
          knowledge base.
        </p>
      </div>

      <div className="space-y-2">
        <input
          type="file"
          accept={ACCEPTED_FILE_TYPES}
          disabled={uploading}
          onChange={handleFileChange}
          className="block w-full text-sm"
        />

        <p className="text-xs text-muted-foreground">
          Supported: PDF, TXT, CSV, XLSX
          {" · "}
          Maximum size:{" "}
          {MAX_UPLOAD_SIZE_MB} MB
        </p>
      </div>

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
            ✓ Document ready
          </div>

          <p className="mt-1 text-muted-foreground">
            Your document has been added
            to the knowledge base and is
            ready for questions.
          </p>

          <div className="mt-3 rounded-md bg-muted p-3">
            <div className="font-medium">
              {
                result.data
                  .original_filename
              }
            </div>

            <div className="text-muted-foreground">
              {formatFileSize(
                result.data.size_bytes,
              )}
            </div>
          </div>
        </div>
      )}
    </section>
  );
}