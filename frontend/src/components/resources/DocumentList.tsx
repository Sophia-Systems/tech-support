import { Trash2, FileText, Globe, Loader2 } from "lucide-react";
import { cn } from "@/components/ui/cn";
import type { DocumentResponse } from "@/types";

interface Props {
  documents: DocumentResponse[];
  onDelete: (id: string) => void;
}

const statusStyles: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800",
  processing: "bg-blue-100 text-blue-800",
  ready: "bg-green-100 text-green-800",
  error: "bg-red-100 text-red-800",
};

export function DocumentList({ documents, onDelete }: Props) {
  if (documents.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-border py-12 text-center text-sm text-muted-foreground">
        No documents yet. Upload a file or add a URL above.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border bg-muted/50">
            <th className="px-4 py-2.5 text-left font-medium">Document</th>
            <th className="px-4 py-2.5 text-left font-medium">Type</th>
            <th className="px-4 py-2.5 text-left font-medium">Status</th>
            <th className="px-4 py-2.5 text-right font-medium">Chunks</th>
            <th className="w-10 px-4 py-2.5"></th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <tr key={doc.id} className="border-b border-border last:border-0 hover:bg-muted/30">
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  {doc.source_type === "web" ? (
                    <Globe className="h-4 w-4 shrink-0 text-muted-foreground" />
                  ) : (
                    <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />
                  )}
                  <span className="truncate font-medium" title={doc.title}>
                    {doc.title}
                  </span>
                </div>
              </td>
              <td className="px-4 py-3 text-muted-foreground">{doc.source_type}</td>
              <td className="px-4 py-3">
                <span
                  className={cn(
                    "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium",
                    statusStyles[doc.status] || "bg-gray-100 text-gray-800",
                  )}
                >
                  {(doc.status === "pending" || doc.status === "processing") && (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  )}
                  {doc.status}
                </span>
              </td>
              <td className="px-4 py-3 text-right tabular-nums text-muted-foreground">
                {doc.chunk_count || "—"}
              </td>
              <td className="px-4 py-3">
                <button
                  onClick={() => onDelete(doc.id)}
                  className="rounded p-1 text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive"
                  title="Delete document"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
