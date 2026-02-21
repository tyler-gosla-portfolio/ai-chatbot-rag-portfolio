"use client";

import { DocumentList } from "../../../components/documents/DocumentList";
import { DocumentUpload } from "../../../components/documents/DocumentUpload";
import { useDocuments } from "../../../hooks/useDocuments";

export default function DocumentsPage() {
  const { data, isLoading, uploadDocument, deleteDocument } = useDocuments();

  return (
    <section className="space-y-6">
      <h1 className="text-2xl font-semibold">Documents</h1>
      <DocumentUpload onUpload={uploadDocument} />
      {isLoading ? <p>Loading documents...</p> : <DocumentList documents={data ?? []} onDelete={deleteDocument} />}
    </section>
  );
}
