const API_BASE = "/api/v1";

export async function createSession(): Promise<{ id: string }> {
  const res = await fetch(`${API_BASE}/sessions`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to create session");
  return res.json();
}

export async function listSessions(): Promise<{ id: string; title?: string }[]> {
  const res = await fetch(`${API_BASE}/sessions`);
  if (!res.ok) throw new Error("Failed to list sessions");
  return res.json();
}

export async function submitFeedback(
  messageId: string,
  rating: number,
  comment?: string,
): Promise<void> {
  const res = await fetch(`${API_BASE}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message_id: messageId, rating, comment }),
  });
  if (!res.ok) throw new Error("Failed to submit feedback");
}
