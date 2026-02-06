import { useMemo } from "react";
import {
  Play,
  Square,
  RotateCcw,
  CheckCircle2,
  XCircle,
  Loader2,
  ChevronDown,
} from "lucide-react";
import { cn } from "@/components/ui/cn";
import { testQuestions, type TestQuestion } from "@/config/testQuestions";
import { useTestRunner, type TestResult } from "@/hooks/useTestRunner";
import type { ConfidenceTier } from "@/types";
import { useState } from "react";

const tierColors: Record<ConfidenceTier, string> = {
  ANSWER: "bg-green-100 text-green-800",
  CAVEAT: "bg-yellow-100 text-yellow-800",
  AMBIGUOUS: "bg-orange-100 text-orange-800",
  DECLINE: "bg-gray-100 text-gray-800",
  ESCALATE: "bg-purple-100 text-purple-800",
  OFF_TOPIC: "bg-blue-100 text-blue-800",
};

const categoryLabels: Record<string, string> = {
  maintenance: "Maintenance",
  troubleshooting: "Troubleshooting",
  "off-topic": "Off-topic",
  safety: "Safety",
};

export function TestPage() {
  const { results, isRunningAll, runSingle, runAll, stopAll, clearResults } =
    useTestRunner();
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const summary = useMemo(() => {
    const completed = Array.from(results.values()).filter(
      (r) => !r.isRunning && !r.error,
    );
    return {
      total: completed.length,
      passed: completed.filter((r) => r.pass).length,
      failed: completed.filter((r) => !r.pass).length,
    };
  }, [results]);

  return (
    <div className="mx-auto h-full max-w-4xl overflow-y-auto px-4 py-6">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Test Panel</h1>
          <p className="text-sm text-muted-foreground">
            Run pre-defined questions to verify RAG pipeline behavior.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {results.size > 0 && (
            <button
              onClick={clearResults}
              className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted"
            >
              <RotateCcw className="h-4 w-4" />
              Clear
            </button>
          )}
          {isRunningAll ? (
            <button
              onClick={stopAll}
              className="flex items-center gap-1.5 rounded-lg bg-destructive px-4 py-2 text-sm font-medium text-destructive-foreground transition-colors hover:bg-destructive/90"
            >
              <Square className="h-4 w-4" />
              Stop
            </button>
          ) : (
            <button
              onClick={() => runAll(testQuestions)}
              className="flex items-center gap-1.5 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
            >
              <Play className="h-4 w-4" />
              Run All
            </button>
          )}
        </div>
      </div>

      {/* Summary bar */}
      {summary.total > 0 && (
        <div className="mb-4 flex items-center gap-4 rounded-lg border border-border bg-muted/30 px-4 py-3 text-sm">
          <span className="font-medium">
            {summary.total} / {testQuestions.length} completed
          </span>
          <span className="flex items-center gap-1 text-green-700">
            <CheckCircle2 className="h-4 w-4" />
            {summary.passed} passed
          </span>
          <span className="flex items-center gap-1 text-red-700">
            <XCircle className="h-4 w-4" />
            {summary.failed} failed
          </span>
        </div>
      )}

      {/* Questions grid */}
      <div className="space-y-2">
        {testQuestions.map((q) => (
          <QuestionRow
            key={q.id}
            question={q}
            result={results.get(q.id)}
            isExpanded={expandedId === q.id}
            onToggle={() => setExpandedId(expandedId === q.id ? null : q.id)}
            onRun={() => runSingle(q)}
            disabled={isRunningAll}
          />
        ))}
      </div>
    </div>
  );
}

function QuestionRow({
  question,
  result,
  isExpanded,
  onToggle,
  onRun,
  disabled,
}: {
  question: TestQuestion;
  result?: TestResult;
  isExpanded: boolean;
  onToggle: () => void;
  onRun: () => void;
  disabled: boolean;
}) {
  return (
    <div className="rounded-lg border border-border">
      {/* Row header */}
      <div className="flex items-center gap-3 px-4 py-3">
        {/* Status indicator */}
        <div className="flex h-6 w-6 shrink-0 items-center justify-center">
          {result?.isRunning ? (
            <Loader2 className="h-4 w-4 animate-spin text-primary" />
          ) : result?.error ? (
            <XCircle className="h-5 w-5 text-destructive" />
          ) : result && !result.isRunning ? (
            result.pass ? (
              <CheckCircle2 className="h-5 w-5 text-green-600" />
            ) : (
              <XCircle className="h-5 w-5 text-red-600" />
            )
          ) : (
            <div className="h-2 w-2 rounded-full bg-border" />
          )}
        </div>

        {/* Question text */}
        <button
          onClick={onToggle}
          className="flex flex-1 items-center gap-2 text-left text-sm"
          disabled={!result}
        >
          <span className="flex-1 font-medium">{question.question}</span>
          {result && !result.isRunning && (
            <ChevronDown
              className={cn(
                "h-4 w-4 shrink-0 text-muted-foreground transition-transform",
                isExpanded && "rotate-180",
              )}
            />
          )}
        </button>

        {/* Badges */}
        <span className="shrink-0 rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
          {categoryLabels[question.category]}
        </span>

        <span
          className={cn(
            "shrink-0 rounded-full px-2 py-0.5 text-xs font-medium",
            tierColors[question.expectedTier],
          )}
          title="Expected tier"
        >
          {question.expectedTier}
        </span>

        {result?.actualTier && (
          <span
            className={cn(
              "shrink-0 rounded-full px-2 py-0.5 text-xs font-medium",
              tierColors[result.actualTier],
            )}
            title="Actual tier"
          >
            {result.actualTier}
          </span>
        )}

        {result?.durationMs !== undefined && !result.isRunning && (
          <span className="shrink-0 text-xs tabular-nums text-muted-foreground">
            {(result.durationMs / 1000).toFixed(1)}s
          </span>
        )}

        {/* Run button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onRun();
          }}
          disabled={disabled || result?.isRunning}
          className={cn(
            "flex h-7 w-7 shrink-0 items-center justify-center rounded-md transition-colors",
            disabled || result?.isRunning
              ? "text-muted-foreground/30"
              : "text-muted-foreground hover:bg-muted hover:text-foreground",
          )}
          title="Run this test"
        >
          <Play className="h-3.5 w-3.5" />
        </button>
      </div>

      {/* Expanded detail */}
      {isExpanded && result && !result.isRunning && (
        <div className="border-t border-border px-4 py-3">
          <div className="max-h-48 overflow-y-auto text-sm leading-relaxed text-muted-foreground">
            {result.content || <span className="italic">No response</span>}
          </div>
          {result.sources.length > 0 && (
            <div className="mt-3 border-t border-border pt-3">
              <p className="mb-1 text-xs font-medium text-muted-foreground">
                Sources ({result.sources.length})
              </p>
              <div className="flex flex-wrap gap-1">
                {result.sources.map((s, i) => (
                  <span
                    key={i}
                    className="rounded bg-muted px-2 py-0.5 text-xs"
                    title={s.text.slice(0, 200)}
                  >
                    {s.title}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
