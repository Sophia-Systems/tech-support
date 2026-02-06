const API_BASE = "/api/v1";

export interface SSECallbacks {
  onMetadata: (data: {
    session_id: string;
    confidence_tier: string;
    message_id: string;
  }) => void;
  onDelta: (content: string) => void;
  onSources: (sources: { title: string; text: string; score: number }[]) => void;
  onDone: (data: { usage: Record<string, number> }) => void;
  onError: (error: string) => void;
}

export async function streamChat(
  message: string,
  sessionId: string | null,
  callbacks: SSECallbacks,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(`${API_BASE}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      session_id: sessionId,
    }),
    signal,
  });

  if (!res.ok) {
    callbacks.onError("Failed to connect to chat service");
    return;
  }

  const reader = res.body?.getReader();
  if (!reader) {
    callbacks.onError("No response stream");
    return;
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    let currentEvent = "";
    for (const line of lines) {
      if (line.startsWith("event: ")) {
        currentEvent = line.slice(7).trim();
      } else if (line.startsWith("data: ") && currentEvent) {
        const data = line.slice(6);
        try {
          const parsed = JSON.parse(data);
          switch (currentEvent) {
            case "metadata":
              callbacks.onMetadata(parsed);
              break;
            case "delta":
              callbacks.onDelta(parsed.content || "");
              break;
            case "sources":
              callbacks.onSources(parsed);
              break;
            case "done":
              callbacks.onDone(parsed);
              break;
            case "error":
              callbacks.onError(parsed.detail || "Unknown error");
              break;
          }
        } catch {
          // Skip malformed JSON
        }
        currentEvent = "";
      }
    }
  }
}
