import { useCallback, useState } from "react";
import { Link } from "lucide-react";
import { cn } from "@/components/ui/cn";

interface Props {
  onSubmit: (url: string) => Promise<void>;
}

export function URLInput({ onSubmit }: Props) {
  const [url, setUrl] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      const trimmed = url.trim();
      if (!trimmed) return;

      setError(null);
      setIsSubmitting(true);
      try {
        await onSubmit(trimmed);
        setUrl("");
      } catch (e) {
        setError(e instanceof Error ? e.message : "Submission failed");
      } finally {
        setIsSubmitting(false);
      }
    },
    [url, onSubmit],
  );

  return (
    <div>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="relative flex-1">
          <Link className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/docs/page"
            className={cn(
              "w-full rounded-lg border border-input bg-background py-2.5 pl-9 pr-3",
              "text-sm placeholder:text-muted-foreground",
              "focus:outline-none focus:ring-2 focus:ring-ring",
            )}
            disabled={isSubmitting}
          />
        </div>
        <button
          type="submit"
          disabled={!url.trim() || isSubmitting}
          className={cn(
            "rounded-lg px-4 py-2.5 text-sm font-medium transition-colors",
            url.trim()
              ? "bg-primary text-primary-foreground hover:bg-primary/90"
              : "bg-muted text-muted-foreground",
          )}
        >
          {isSubmitting ? "Adding..." : "Add URL"}
        </button>
      </form>
      {error && (
        <p className="mt-2 text-sm text-destructive">{error}</p>
      )}
    </div>
  );
}
