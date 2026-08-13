"use client";

import type { ReactNode } from "react";
import { demoPdf } from "@/lib/demo";

function bytesToPdfUrl(bytes: Uint8Array) {
  const copy = Uint8Array.from(bytes);
  const blob = new Blob([copy], { type: "application/pdf" });
  return URL.createObjectURL(blob);
}

export function ArtifactLink({ href, children }: { href?: string; children: ReactNode }) {
  if (!href) return null;
  const artifactPath = href;

  async function openArtifact() {
    const filename = artifactPath.split("/").at(-1) ?? "acreops-demo.pdf";
    try {
      const res = await fetch(`/api/backend${artifactPath}`, { cache: "no-store" });
      if (res.ok) {
        const blob = await res.blob();
        if (blob.size > 0 && (blob.type.includes("pdf") || blob.type.includes("octet-stream"))) {
          window.open(URL.createObjectURL(blob), "_blank", "noopener,noreferrer");
          return;
        }
      }
    } catch {
      // Hosted previews still need a downloadable packet if the BFF is unreachable.
    }
    const url = bytesToPdfUrl(demoPdf(filename));
    window.open(url, "_blank", "noopener,noreferrer");
  }

  return (
    <button
      type="button"
      onClick={() => void openArtifact()}
      className="inline-flex border border-ink px-3 py-2 text-sm text-ink transition hover:bg-ink hover:text-paper"
    >
      {children} ↗
    </button>
  );
}
