export interface DocumentSummary {
  document_id: string;
  original_filename: string;
  content_type: string;
  size_bytes: number;
  uploaded_at: string;
  chunk_count: number;
  status: string;
}

export interface DocumentListResponse {
  documents: DocumentSummary[];
}