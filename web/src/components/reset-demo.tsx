"use client";

export function resetDemo() {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.clear();
  } catch {
    // Ignore private-mode storage failures; a reload still restores sample forms.
  }
  window.location.assign("/");
}

export function ResetDemoButton({ className = "" }: { className?: string }) {
  return (
    <button
      type="button"
      onClick={resetDemo}
      className={`inline-flex shrink-0 items-center justify-center border border-rule px-3 py-1.5 text-[12px] text-ink-soft transition hover:border-ink hover:text-ink ${className}`}
    >
      Reset demo
    </button>
  );
}
