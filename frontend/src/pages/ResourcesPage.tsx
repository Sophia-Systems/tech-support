import { useDocuments } from "@/hooks/useDocuments";
import { UploadDropzone } from "@/components/resources/UploadDropzone";
import { URLInput } from "@/components/resources/URLInput";
import { DocumentList } from "@/components/resources/DocumentList";
import { Loader2 } from "lucide-react";

export function ResourcesPage() {
  const { documents, isLoading, error, upload, addURL, remove } = useDocuments();

  return (
    <div className="mx-auto h-full max-w-3xl overflow-y-auto px-4 py-6">
      <div className="mb-6">
        <h1 className="text-lg font-semibold">Knowledge Base</h1>
        <p className="text-sm text-muted-foreground">
          Upload documents or add URLs to expand the knowledge base.
        </p>
      </div>

      <div className="mb-6 grid gap-4 sm:grid-cols-2">
        <UploadDropzone onUpload={async (f) => { await upload(f); }} />
        <URLInput onSubmit={async (u) => { await addURL(u); }} />
      </div>

      {error && (
        <p className="mb-4 text-sm text-destructive">{error}</p>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : (
        <DocumentList documents={documents} onDelete={remove} />
      )}
    </div>
  );
}
