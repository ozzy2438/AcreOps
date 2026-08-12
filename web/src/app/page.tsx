import Link from "next/link";
import { PageIntro, Panel, Stat } from "@/components/ui";
import { AGENTS } from "@/lib/agents";

const API = process.env.ACREOPS_API_URL ?? "http://127.0.0.1:8000";

async function loadDesk() {
  try {
    const [health, parcels, vendors, permits, tenants] = await Promise.all([
      fetch(`${API}/health`, { cache: "no-store" }).then((r) => r.json()),
      fetch(`${API}/catalog/parcels`, { cache: "no-store" }).then((r) => r.json()),
      fetch(`${API}/catalog/vendors`, { cache: "no-store" }).then((r) => r.json()),
      fetch(`${API}/catalog/permits`, { cache: "no-store" }).then((r) => r.json()),
      fetch(`${API}/catalog/tenants`, { cache: "no-store" }).then((r) => r.json()),
    ]);
    return { ok: true as const, health, parcels, vendors, permits, tenants };
  } catch {
    return { ok: false as const };
  }
}

export default async function DeskPage() {
  const desk = await loadDesk();

  return (
    <>
      <PageIntro kicker="Operator desk" title="Five agents. One field book.">
        Work that used to live in a broker binder, a maintenance inbox, a city portal,
        a weekly flyover, and a renewal spreadsheet — now a short run from this desk.
      </PageIntro>

      {desk.ok ? (
        <div className="mb-8 grid grid-cols-2 gap-3 md:grid-cols-5">
          <Stat label="Parcels" value={desk.parcels.length} />
          <Stat label="Vendors" value={desk.vendors.length} />
          <Stat label="Permits" value={desk.permits.length} />
          <Stat label="Leases" value={desk.tenants.length} />
          <Stat label="API" value={desk.health.version ?? "ok"} tone="sage" />
        </div>
      ) : (
        <Panel className="mb-8">
          <p className="text-sm text-ink-soft">
            API is quiet. Start it with <code className="font-mono text-ink">make api</code> and
            refresh — the desk still works; live counts will appear.
          </p>
        </Panel>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        {AGENTS.map((agent) => (
          <Link key={agent.href} href={agent.href} className="group block">
            <Panel className="h-full transition group-hover:border-ink">
              <div className="flex items-start justify-between gap-4">
                <p className="font-mono text-[11px] tracking-[0.16em] text-copper">{agent.code}</p>
                <span className="text-lg text-ink-soft">{agent.mark}</span>
              </div>
              <h2 className="mt-3 font-serif text-2xl text-ink">{agent.title}</h2>
              <p className="mt-2 text-sm leading-relaxed text-ink-soft">
                <span className="text-ink">Was:</span> {agent.replaces}
              </p>
              <p className="mt-1 text-sm leading-relaxed text-ink-soft">
                <span className="text-ink">Now:</span> {agent.produces}
              </p>
            </Panel>
          </Link>
        ))}
      </div>
    </>
  );
}
