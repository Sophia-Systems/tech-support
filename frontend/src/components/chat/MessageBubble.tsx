import ReactMarkdown from "react-markdown";
import { Bot, User } from "lucide-react";
import type { ChatMessage } from "@/types";
import { cn } from "@/components/ui/cn";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { FeedbackButtons } from "./FeedbackButtons";
import { SourceCard } from "./SourceCard";

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={cn("flex gap-3", isUser && "flex-row-reverse")}>
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
          isUser ? "bg-primary text-primary-foreground" : "bg-muted",
        )}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>

      <div className={cn("flex max-w-[75%] flex-col gap-1", isUser && "items-end")}>
        <div
          className={cn(
            "rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
            isUser
              ? "bg-primary text-primary-foreground"
              : "bg-muted text-foreground",
          )}
        >
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            <div className="prose prose-sm max-w-none dark:prose-invert">
              <ReactMarkdown>{message.content}</ReactMarkdown>
              {message.isStreaming && (
                <span className="ml-0.5 inline-block h-4 w-1 animate-pulse bg-foreground/70" />
              )}
            </div>
          )}
        </div>

        {!isUser && !message.isStreaming && (
          <div className="flex items-center gap-2 px-1">
            {message.confidenceTier && (
              <ConfidenceBadge tier={message.confidenceTier} />
            )}
            <FeedbackButtons messageId={message.id} />
          </div>
        )}

        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-1 flex w-full flex-col gap-1">
            {message.sources.map((source, i) => (
              <SourceCard key={i} source={source} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
