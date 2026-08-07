export interface StorageResult {
  document_id: string;
  original_filename: string;
  stored_filename: string;
  file_path: string;
  content_type: string;
  size_bytes: number;
}

export interface UploadResponse {
  success: boolean;
  message: string;
  data: StorageResult;
}