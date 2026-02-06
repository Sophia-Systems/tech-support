import { useCallback, useEffect, useRef, useState } from "react";
import {
  listDocuments,
  uploadDocument,
  submitURL,
  deleteDocument,
} from "@/lib/api";
import type { DocumentResponse } from "@/types";

export function useDocuments() {
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetch = useCallback(async () => {
    try {
      const docs = await listDocuments();
      setDocuments(docs);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to fetch documents");
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Poll while any doc is pending/processing
  useEffect(() => {
    fetch();
  }, [fetch]);

  useEffect(() => {
    const hasPending = documents.some(
      (d) => d.status === "pending" || d.status === "processing",
    );
    if (hasPending && !pollRef.current) {
      pollRef.current = setInterval(fetch, 3000);
    } else if (!hasPending && pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [documents, fetch]);

  const upload = useCallback(
    async (file: File) => {
      const doc = await uploadDocument(file);
      setDocuments((prev) => [doc, ...prev]);
      return doc;
    },
    [],
  );

  const addURL = useCallback(
    async (url: string, title?: string) => {
      const doc = await submitURL(url, title);
      setDocuments((prev) => [doc, ...prev]);
      return doc;
    },
    [],
  );

  const remove = useCallback(async (id: string) => {
    await deleteDocument(id);
    setDocuments((prev) => prev.filter((d) => d.id !== id));
  }, []);

  return { documents, isLoading, error, upload, addURL, remove, refresh: fetch };
}
