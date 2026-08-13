import type { ReactNode } from "react";

export function PageIntro({
  kicker,
  title,
  children,
}: {
  kicker: string;
  title: string;
  children?: ReactNode;
}) {
  return (
    <div className="mb-8 max-w-2xl">
      <p className="mb-2 text-[11px] font-medium uppercase tracking-[0.2em] text-copper">{kicker}</p>
      <h1 className="font-serif text-3xl tracking-tight text-ink sm:text-4xl">{title}</h1>
      {children ? <p className="mt-3 text-[15px] leading-relaxed text-ink-soft">{children}</p> : null}
    </div>
  );
}

export function Panel({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <section className={`border border-rule bg-white/80 p-5 shadow-[0_1px_0_rgb(18_36_58/0.04)] ${className}`}>
      {children}
    </section>
  );
}

export function Field({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-[11px] font-medium uppercase tracking-[0.14em] text-ink-soft">
        {label}
      </span>
      {children}
    </label>
  );
}

const input =
  "w-full border border-rule bg-white px-3 py-2 text-sm text-ink outline-none transition focus:border-ink";

export function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={`${input} ${props.className ?? ""}`} />;
}

export function Select(props: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return <select {...props} className={`${input} ${props.className ?? ""}`} />;
}

export function Textarea(props: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea {...props} className={`${input} min-h-28 ${props.className ?? ""}`} />;
}

export function Button({
  children,
  pending,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { pending?: boolean }) {
  return (
    <button
      {...props}
      disabled={pending || props.disabled}
      className={`inline-flex items-center justify-center bg-ink px-4 py-2 text-sm text-paper transition hover:bg-copper disabled:cursor-wait disabled:opacity-60 ${
        props.className ?? ""
      }`}
    >
      {pending ? "Running…" : children}
    </button>
  );
}

export function Stat({
  label,
  value,
  tone = "ink",
}: {
  label: string;
  value: ReactNode;
  tone?: "ink" | "sage" | "clay" | "amber" | "copper";
}) {
  const color = {
    ink: "text-ink",
    sage: "text-sage",
    clay: "text-clay",
    amber: "text-amber",
    copper: "text-copper",
  }[tone];
  return (
    <div className="border border-rule bg-white/70 px-4 py-3">
      <p className="text-[10px] uppercase tracking-[0.16em] text-ink-soft">{label}</p>
      <p className={`mt-1 font-serif text-2xl leading-none ${color}`}>{value}</p>
    </div>
  );
}

export function Pill({ children, tone = "ink" }: { children: ReactNode; tone?: "ink" | "sage" | "clay" | "amber" }) {
  const cls = {
    ink: "bg-paper-2 text-ink",
    sage: "bg-sage-soft text-sage",
    clay: "bg-[#f3ddd8] text-clay",
    amber: "bg-[#f4e6c4] text-amber",
  }[tone];
  return (
    <span className={`inline-flex px-2 py-0.5 text-[11px] uppercase tracking-[0.12em] ${cls}`}>
      {children}
    </span>
  );
}

export function ErrorNote({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <p className="border border-clay/30 bg-[#f8ece9] px-3 py-2 text-sm text-clay">
      {message}. Start the API with <code className="font-mono">make api</code>.
    </p>
  );
}

export function ArtifactLink({ href, children }: { href?: string; children: ReactNode }) {
  if (!href) return null;
  const target = href.startsWith("/") ? `/api/backend${href}` : null;
  if (!target) {
    return <p className="font-mono text-[11px] text-ink-soft">Artifact: {href}</p>;
  }
  return (
    <a
      href={target}
      target="_blank"
      rel="noreferrer"
      className="inline-flex border border-ink px-3 py-2 text-sm text-ink transition hover:bg-ink hover:text-paper"
    >
      {children} ↗
    </a>
  );
}

export function Audit({ events }: { events: { action: string; timestamp?: string }[] }) {
  if (!events.length) return null;
  return (
    <ol className="space-y-1 font-mono text-[12px] text-ink-soft">
      {events.map((event, i) => (
        <li key={`${event.action}-${i}`} className="flex gap-3">
          <span className="text-copper">{String(i + 1).padStart(2, "0")}</span>
          <span>{event.action.replaceAll("_", " ")}</span>
        </li>
      ))}
    </ol>
  );
}

export function Table({
  columns,
  rows,
}: {
  columns: string[];
  rows: ReactNode[][];
}) {
  return (
    <div className="overflow-x-auto border border-rule">
      <table className="w-full text-left text-sm">
        <thead className="bg-ink text-[11px] uppercase tracking-[0.12em] text-paper">
          <tr>
            {columns.map((col) => (
              <th key={col} className="px-3 py-2 font-medium">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-t border-rule bg-white/70">
              {row.map((cell, j) => (
                <td key={j} className="px-3 py-2 align-top">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
