import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import { MessageSquare, FolderOpen, FlaskConical } from "lucide-react";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { ChatPage } from "@/pages/ChatPage";
import { ResourcesPage } from "@/pages/ResourcesPage";
import { TestPage } from "@/pages/TestPage";
import { cn } from "@/components/ui/cn";

const navItems = [
  { to: "/", icon: MessageSquare, label: "Chat" },
  { to: "/resources", icon: FolderOpen, label: "Resources" },
  { to: "/test", icon: FlaskConical, label: "Test" },
] as const;

export function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <div className="flex h-full">
          {/* Sidebar */}
          <nav className="flex w-14 flex-col items-center gap-1 border-r border-border bg-muted/40 py-3">
            {navItems.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/"}
                className={({ isActive }) =>
                  cn(
                    "flex h-10 w-10 items-center justify-center rounded-lg transition-colors",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground",
                  )
                }
                title={label}
              >
                <Icon className="h-5 w-5" />
              </NavLink>
            ))}
          </nav>

          {/* Main content */}
          <main className="flex-1 overflow-hidden">
            <Routes>
              <Route path="/" element={<ChatPage />} />
              <Route path="/resources" element={<ResourcesPage />} />
              <Route path="/test" element={<TestPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
