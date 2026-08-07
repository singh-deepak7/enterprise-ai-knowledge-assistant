import type { ChatRequest } from "@/types/chat";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://localhost:8000/api/v1";


export async function streamChat(
  request: ChatRequest,
  onMessage: (data: unknown) => void,
): Promise<void> {

  const response = await fetch(
    `${API_BASE_URL}/chat/stream`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    },
  );


  if (!response.ok) {
    throw new Error(
      `Streaming request failed: ${response.status}`,
    );
  }


  if (!response.body) {
    throw new Error(
      "Streaming response body missing",
    );
  }


  const reader =
    response.body.getReader();


  const decoder =
    new TextDecoder();


  let buffer = "";


  while (true) {
    const {
      done,
      value,
    } = await reader.read();


    if (done) {
      break;
    }


    buffer += decoder.decode(
      value,
      {
        stream: true,
      },
    );


    const events =
      buffer.split("\n\n");


    buffer =
      events.pop() ?? "";


    for (const event of events) {

      if (!event.startsWith("data:")) {
        continue;
      }


      const payload =
        event.replace(
          "data:",
          "",
        ).trim();


      if (!payload) {
        continue;
      }


      onMessage(
        JSON.parse(payload),
      );
    }
  }
}