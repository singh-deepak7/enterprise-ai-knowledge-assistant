import { api } from "./api";
import type { ChatRequest, ChatResponse } from "@/types/chat";

const CHAT_ENDPOINT = "/chat";

export const chatService = {
  ask(request: ChatRequest): Promise<ChatResponse> {
    return api.post<ChatResponse>(CHAT_ENDPOINT, request);
  },
};