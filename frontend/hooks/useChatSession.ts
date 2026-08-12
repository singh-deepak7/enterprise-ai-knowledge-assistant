"use client";

import { useCallback, useMemo, useSyncExternalStore } from "react";

import type { ChatMessage } from "@/types/message";

const SESSION_ID_KEY =
  "enterprise-ai-chat-session-id";

const MESSAGES_KEY =
  "enterprise-ai-chat-messages";

const SESSION_CHANGE_EVENT =
  "enterprise-ai-chat-session-change";

const SERVER_SNAPSHOT = JSON.stringify({
  sessionId: "",
  messages: "[]",
});

interface StoredChatMessage
  extends Omit<ChatMessage, "createdAt"> {
  createdAt: string;
}

interface ChatSessionSnapshot {
  sessionId: string;
  messages: string;
}

type MessageUpdater =
  | ChatMessage[]
  | ((
      previous: ChatMessage[],
    ) => ChatMessage[]);

function getServerSnapshot(): string {
  return SERVER_SNAPSHOT;
}

function getClientSnapshot(): string {
  return JSON.stringify({
    sessionId:
      sessionStorage.getItem(
        SESSION_ID_KEY,
      ) ?? "",

    messages:
      sessionStorage.getItem(
        MESSAGES_KEY,
      ) ?? "[]",
  });
}

function subscribe(
  callback: () => void,
): () => void {
  function handleStorage(
    event: StorageEvent,
  ) {
    if (
      event.key === SESSION_ID_KEY ||
      event.key === MESSAGES_KEY
    ) {
      callback();
    }
  }

  window.addEventListener(
    "storage",
    handleStorage,
  );

  window.addEventListener(
    SESSION_CHANGE_EVENT,
    callback,
  );

  return () => {
    window.removeEventListener(
      "storage",
      handleStorage,
    );

    window.removeEventListener(
      SESSION_CHANGE_EVENT,
      callback,
    );
  };
}

function notifySubscribers(): void {
  window.dispatchEvent(
    new Event(
      SESSION_CHANGE_EVENT,
    ),
  );
}

function parseMessages(
  rawMessages: string,
): ChatMessage[] {
  try {
    const parsed = JSON.parse(
      rawMessages,
    ) as StoredChatMessage[];

    if (!Array.isArray(parsed)) {
      return [];
    }

    return parsed.map(
      (message) => ({
        ...message,
        createdAt: new Date(
          message.createdAt,
        ),

        // Workflow status is transient and
        // should not survive a refresh.
        status: undefined,
      }),
    );
  } catch {
    return [];
  }
}

function readMessagesFromStorage(): ChatMessage[] {
  const stored =
    sessionStorage.getItem(
      MESSAGES_KEY,
    ) ?? "[]";

  return parseMessages(stored);
}

function persistMessages(
  messages: ChatMessage[],
): void {
  sessionStorage.setItem(
    MESSAGES_KEY,
    JSON.stringify(messages),
  );

  notifySubscribers();
}

export function useChatSession() {
  const snapshot =
    useSyncExternalStore(
      subscribe,
      getClientSnapshot,
      getServerSnapshot,
    );

  const parsedSnapshot =
    useMemo<ChatSessionSnapshot>(
      () =>
        JSON.parse(
          snapshot,
        ) as ChatSessionSnapshot,
      [snapshot],
    );

  const messages = useMemo(
    () =>
      parseMessages(
        parsedSnapshot.messages,
      ),
    [parsedSnapshot.messages],
  );

  const ensureSessionId =
    useCallback((): string => {
      const existingSessionId =
        sessionStorage.getItem(
          SESSION_ID_KEY,
        );

      if (existingSessionId) {
        return existingSessionId;
      }

      const newSessionId =
        crypto.randomUUID();

      sessionStorage.setItem(
        SESSION_ID_KEY,
        newSessionId,
      );

      notifySubscribers();

      return newSessionId;
    }, []);

  const setMessages = useCallback(
    (updater: MessageUpdater) => {
      const previous =
        readMessagesFromStorage();

      const nextMessages =
        typeof updater === "function"
          ? updater(previous)
          : updater;

      persistMessages(
        nextMessages,
      );
    },
    [],
  );

  const startNewChat =
    useCallback(() => {
      const newSessionId =
        crypto.randomUUID();

      sessionStorage.setItem(
        SESSION_ID_KEY,
        newSessionId,
      );

      sessionStorage.removeItem(
        MESSAGES_KEY,
      );

      notifySubscribers();
    }, []);

  return {
    sessionId:
      parsedSnapshot.sessionId,

    messages,

    setMessages,

    ensureSessionId,

    startNewChat,
  };
}