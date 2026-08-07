export interface DocumentSummary {
  document_id: string;
  original_filename: string;
  content_type: string;
  size_bytes: number;
}

export interface DocumentListResponse {
  documents: DocumentSummary[];
}