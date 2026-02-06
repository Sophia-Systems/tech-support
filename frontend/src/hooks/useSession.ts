import { useCallback, useEffect, useState } from "react";
import { createSession, listSessions } from "@/lib/api";
import type { ChatSession } from "@/types";

export function useSession() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);

  const fetchSessions = useCallback(async () => {
    try {
      const data = await listSessions();
      setSessions(data as ChatSession[]);
    } catch {
      // Silently handle — sessions list is non-critical
    }
  }, []);

  const startNewSession = useCallback(async () => {
    try {
      const session = await createSession();
      setCurrentSessionId(session.id);
      await fetchSessions();
      return session.id;
    } catch {
      return null;
    }
  }, [fetchSessions]);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  return {
    sessions,
    currentSessionId,
    setCurrentSessionId,
    startNewSession,
    refreshSessions: fetchSessions,
  };
}
