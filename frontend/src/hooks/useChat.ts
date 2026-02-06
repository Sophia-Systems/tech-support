import { useCallback, useRef, useState } from "react";
import { streamChat } from "@/lib/sse";
import type { ChatMessage, ConfidenceTier, Source } from "@/types";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return;

      const userMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content,
      };

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "",
        isStreaming: true,
      };

      setMessages((prev) => [...prev, userMessage, assistantMessage]);
      setIsLoading(true);

      const controller = new AbortController();
      abortRef.current = controller;

      let currentContent = "";
      let messageId = assistantMessage.id;

      await streamChat(
        content,
        sessionId,
        {
          onMetadata: (data) => {
            if (data.session_id) setSessionId(data.session_id);
            messageId = data.message_id || messageId;
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantMessage.id
                  ? {
                      ...m,
                      id: messageId,
                      confidenceTier: data.confidence_tier as ConfidenceTier,
                    }
                  : m,
              ),
            );
          },
          onDelta: (delta) => {
            currentContent += delta;
            setMessages((prev) =>
              prev.map((m) =>
                m.id === messageId ? { ...m, content: currentContent } : m,
              ),
            );
          },
          onSources: (sources: Source[]) => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === messageId ? { ...m, sources } : m,
              ),
            );
          },
          onDone: () => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === messageId ? { ...m, isStreaming: false } : m,
              ),
            );
            setIsLoading(false);
          },
          onError: (error) => {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === messageId
                  ? {
                      ...m,
                      content: `Error: ${error}`,
                      isStreaming: false,
                    }
                  : m,
              ),
            );
            setIsLoading(false);
          },
        },
        controller.signal,
      );
    },
    [isLoading, sessionId],
  );

  const stopStreaming = useCallback(() => {
    abortRef.current?.abort();
    setIsLoading(false);
    setMessages((prev) =>
      prev.map((m) => (m.isStreaming ? { ...m, isStreaming: false } : m)),
    );
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setSessionId(null);
  }, []);

  return {
    messages,
    isLoading,
    sessionId,
    sendMessage,
    stopStreaming,
    clearMessages,
  };
}
