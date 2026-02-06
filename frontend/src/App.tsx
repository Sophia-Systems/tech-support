import { ChatWindow } from "@/components/chat/ChatWindow";
import { ErrorBoundary } from "@/components/ErrorBoundary";

export function App() {
  return (
    <ErrorBoundary>
      <div className="mx-auto h-full max-w-3xl">
        <ChatWindow />
      </div>
    </ErrorBoundary>
  );
}
