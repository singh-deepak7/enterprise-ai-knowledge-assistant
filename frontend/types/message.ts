import type { ChatSource } from "./chat";

export type MessageRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;

  confidenceScore?: number;

  sources?: ChatSource[];

  status?: string;

  createdAt: Date;
}