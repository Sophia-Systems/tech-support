import { useCallback, useRef, useState } from "react";
import { streamChat } from "@/lib/sse";
import type { ConfidenceTier, Source } from "@/types";
import type { TestQuestion } from "@/config/testQuestions";

export interface TestResult {
  questionId: string;
  actualTier: ConfidenceTier | null;
  content: string;
  sources: Source[];
  durationMs: number;
  pass: boolean;
  isRunning: boolean;
  error: string | null;
}

export function useTestRunner() {
  const [results, setResults] = useState<Map<string, TestResult>>(new Map());
  const [isRunningAll, setIsRunningAll] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const runSingle = useCallback(
    async (question: TestQuestion): Promise<TestResult> => {
      const startTime = Date.now();

      // Mark as running
      const initialResult: TestResult = {
        questionId: question.id,
        actualTier: null,
        content: "",
        sources: [],
        durationMs: 0,
        pass: false,
        isRunning: true,
        error: null,
      };

      setResults((prev) => new Map(prev).set(question.id, initialResult));

      return new Promise<TestResult>((resolve) => {
        const controller = new AbortController();
        abortRef.current = controller;

        let content = "";
        let tier: ConfidenceTier | null = null;
        let sources: Source[] = [];

        streamChat(
          question.question,
          null, // fresh session each time
          {
            onMetadata: (data) => {
              tier = data.confidence_tier as ConfidenceTier;
              setResults((prev) => {
                const r = prev.get(question.id);
                if (!r) return prev;
                return new Map(prev).set(question.id, { ...r, actualTier: tier });
              });
            },
            onDelta: (delta) => {
              content += delta;
              setResults((prev) => {
                const r = prev.get(question.id);
                if (!r) return prev;
                return new Map(prev).set(question.id, { ...r, content });
              });
            },
            onSources: (s) => {
              sources = s as Source[];
              setResults((prev) => {
                const r = prev.get(question.id);
                if (!r) return prev;
                return new Map(prev).set(question.id, { ...r, sources });
              });
            },
            onDone: () => {
              const duration = Date.now() - startTime;
              const pass = tier !== null && question.acceptableTiers.includes(tier);
              const result: TestResult = {
                questionId: question.id,
                actualTier: tier,
                content,
                sources,
                durationMs: duration,
                pass,
                isRunning: false,
                error: null,
              };
              setResults((prev) => new Map(prev).set(question.id, result));
              resolve(result);
            },
            onError: (error) => {
              const duration = Date.now() - startTime;
              const result: TestResult = {
                questionId: question.id,
                actualTier: tier,
                content,
                sources,
                durationMs: duration,
                pass: false,
                isRunning: false,
                error,
              };
              setResults((prev) => new Map(prev).set(question.id, result));
              resolve(result);
            },
          },
          controller.signal,
        );
      });
    },
    [],
  );

  const runAll = useCallback(
    async (questions: TestQuestion[]) => {
      setIsRunningAll(true);
      setResults(new Map());

      // Sequential to avoid overwhelming the LLM
      for (const q of questions) {
        if (abortRef.current?.signal.aborted) break;
        await runSingle(q);
      }

      setIsRunningAll(false);
    },
    [runSingle],
  );

  const stopAll = useCallback(() => {
    abortRef.current?.abort();
    setIsRunningAll(false);
    setResults((prev) => {
      const next = new Map(prev);
      for (const [id, r] of next) {
        if (r.isRunning) {
          next.set(id, { ...r, isRunning: false, error: "Aborted" });
        }
      }
      return next;
    });
  }, []);

  const clearResults = useCallback(() => {
    setResults(new Map());
  }, []);

  return { results, isRunningAll, runSingle, runAll, stopAll, clearResults };
}
