"use client";

import type { Document } from "../../lib/types";

type Props = {
  documents: Document[];
  onDelete: (id: string) => Promise<void>;
};

export function DocumentList({ documents, onDelete }: Props) {
  if (!documents.length) {
    return <p className="text-slate-500">No documents uploaded yet.</p>;
  }

  return (
    <ul className="space-y-3">
      {documents.map((doc) => (
        <li key={doc.id} className="bg-white p-4 border rounded-lg flex justify-between items-center">
          <div>
            <p className="font-semibold">{doc.filename}</p>
            <p className="text-sm text-slate-500">
              {doc.status} • {doc.chunk_count} chunks • {doc.total_tokens} tokens
            </p>
          </div>
          <button className="px-3 py-1 bg-rose-600 text-white rounded" onClick={() => onDelete(doc.id)}>
            Delete
          </button>
        </li>
      ))}
    </ul>
  );
}
