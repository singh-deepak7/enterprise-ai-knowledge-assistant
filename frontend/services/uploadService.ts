import type { UploadResponse } from "@/types/upload";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://localhost:8000/api/v1";

interface ApiErrorResponse {
  detail?: string;
  message?: string;
  error?: {
    code?: string;
    message?: string;
  };
}

export async function uploadDocument(
  file: File,
): Promise<UploadResponse> {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/upload`,
    {
      method: "POST",
      body: formData,
    },
  );

  if (!response.ok) {
    let message = "Document upload failed.";

    try {
      const error =
        (await response.json()) as ApiErrorResponse;

      message =
        error.error?.message ??
        error.detail ??
        error.message ??
        message;
    } catch {
      // Keep the default message when the
      // backend response is not JSON.
    }

    throw new Error(message);
  }

  return (await response.json()) as UploadResponse;
}