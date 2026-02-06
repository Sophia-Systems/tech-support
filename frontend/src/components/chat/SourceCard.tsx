import { useState } from "react";
import { ChevronDown, ChevronUp, FileText } from "lucide-react";
import type { Source } from "@/types";
import { cn } from "@/components/ui/cn";

interface SourceCardProps {
  source: Source;
}

export function SourceCard({ source }: SourceCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="rounded-md border border-border bg-card text-card-foreground">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm transition-colors hover:bg-muted/50"
      >
        <FileText className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
        <span className="flex-1 truncate font-medium">{source.title}</span>
        <span className="text-xs text-muted-foreground">
          {Math.round(source.score * 100)}%
        </span>
        {expanded ? (
          <ChevronUp className="h-3.5 w-3.5 text-muted-foreground" />
        ) : (
          <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />
        )}
      </button>
      <div
        className={cn(
          "overflow-hidden transition-all duration-200",
          expanded ? "max-h-48" : "max-h-0",
        )}
      >
        <div className="border-t border-border px-3 py-2 text-xs text-muted-foreground">
          {source.text}
        </div>
      </div>
    </div>
  );
}
