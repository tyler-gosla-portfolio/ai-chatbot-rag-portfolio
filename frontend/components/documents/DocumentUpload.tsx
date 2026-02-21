"use client";

import { useState } from "react";

type Props = {
  onUpload: (file: File) => Promise<void>;
};

export function DocumentUpload({ onUpload }: Props) {
  const [busy, setBusy] = useState(false);

  async function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true);
    try {
      await onUpload(file);
    } finally {
      setBusy(false);
    }
  }

  return (
    <label className="flex items-center gap-3 p-4 border rounded-lg bg-white">
      <span className="font-medium">Upload document</span>
      <input data-testid="upload-input" type="file" accept=".txt,.md,.pdf" onChange={onFileChange} disabled={busy} />
    </label>
  );
}
