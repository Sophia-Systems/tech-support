export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  confidenceTier?: ConfidenceTier;
  sources?: Source[];
  isStreaming?: boolean;
}

export type ConfidenceTier =
  | "ANSWER"
  | "CAVEAT"
  | "AMBIGUOUS"
  | "DECLINE"
  | "ESCALATE"
  | "OFF_TOPIC";

export interface Source {
  title: string;
  text: string;
  url?: string;
  score: number;
}

export interface ChatSession {
  id: string;
  title?: string;
  created_at: string;
  updated_at: string;
}

export interface SSEEvent {
  event: "metadata" | "delta" | "sources" | "done" | "error";
  data: string;
}
