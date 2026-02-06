import { cn } from "@/components/ui/cn";
import type { ConfidenceTier } from "@/types";

const tierConfig: Record<
  ConfidenceTier,
  { label: string; className: string }
> = {
  ANSWER: { label: "Confident", className: "bg-green-100 text-green-800" },
  CAVEAT: { label: "Partial match", className: "bg-yellow-100 text-yellow-800" },
  AMBIGUOUS: {
    label: "Clarifying",
    className: "bg-blue-100 text-blue-800",
  },
  DECLINE: { label: "Low confidence", className: "bg-orange-100 text-orange-800" },
  ESCALATE: { label: "Escalated", className: "bg-red-100 text-red-800" },
  OFF_TOPIC: {
    label: "Off topic",
    className: "bg-gray-100 text-gray-600",
  },
};

interface ConfidenceBadgeProps {
  tier: ConfidenceTier;
}

export function ConfidenceBadge({ tier }: ConfidenceBadgeProps) {
  const config = tierConfig[tier];
  if (!config) return null;

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
        config.className,
      )}
    >
      {config.label}
    </span>
  );
}
