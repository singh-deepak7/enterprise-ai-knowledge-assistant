export interface ChatRequest {
  question: string;
  session_id?: string;
}

export interface ChatSource {
  source: string;
  page: number;
  chunk: string | null;
}

export interface ChatResponse {
  answer: string;
  sources: ChatSource[];
}