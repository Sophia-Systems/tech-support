import { useState } from "react";
import { ThumbsUp, ThumbsDown } from "lucide-react";
import { submitFeedback } from "@/lib/api";
import { cn } from "@/components/ui/cn";

interface FeedbackButtonsProps {
  messageId: string;
}

export function FeedbackButtons({ messageId }: FeedbackButtonsProps) {
  const [submitted, setSubmitted] = useState<"up" | "down" | null>(null);

  const handleFeedback = async (rating: "up" | "down") => {
    if (submitted) return;
    setSubmitted(rating);
    try {
      await submitFeedback(messageId, rating === "up" ? 5 : 1);
    } catch {
      setSubmitted(null);
    }
  };

  return (
    <div className="flex items-center gap-1">
      <button
        onClick={() => handleFeedback("up")}
        disabled={submitted !== null}
        className={cn(
          "rounded p-1 transition-colors hover:bg-green-50",
          submitted === "up" && "bg-green-100 text-green-700",
          submitted !== null && submitted !== "up" && "opacity-30",
        )}
        aria-label="Helpful"
      >
        <ThumbsUp className="h-3.5 w-3.5" />
      </button>
      <button
        onClick={() => handleFeedback("down")}
        disabled={submitted !== null}
        className={cn(
          "rounded p-1 transition-colors hover:bg-red-50",
          submitted === "down" && "bg-red-100 text-red-700",
          submitted !== null && submitted !== "down" && "opacity-30",
        )}
        aria-label="Not helpful"
      >
        <ThumbsDown className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}
