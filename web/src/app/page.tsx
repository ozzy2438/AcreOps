import Link from "next/link";
import { PageIntro, Panel, SafetyNote, Stat } from "@/components/ui";
import { ResetDemoButton } from "@/components/reset-demo";
import { AGENTS } from "@/lib/agents";
import { DEMO_PARCELS, DEMO_PERMITS, DEMO_TENANTS, DEMO_VENDORS } from "@/lib/demo";

const API = process.env.ACREOPS_API_URL;

async function loadDesk() {
  if (!API) {
    return {
      health: { version: "demo", mode: "interactive_demo" },
      parcels: DEMO_PARCELS,
      vendors: DEMO_VENDORS,
      permits: DEMO_PERMITS,
      tenants: DEMO_TENANTS,
    };
  }
  try {
    const [health, parcels, vendors, permits, tenants] = await Promise.all([
      fetch(`${API}/health`, { cache: "no-store" }).then((r) => r.json()),
      fetch(`${API}/catalog/parcels`, { cache: "no-store" }).then((r) => r.json()),
      fetch(`${API}/catalog/vendors`, { cache: "no-store" }).then((r) => r.json()),
      fetch(`${API}/catalog/permits`, { cache: "no-store" }).then((r) => r.json()),
      fetch(`${API}/catalog/tenants`, { cache: "no-store" }).then((r) => r.json()),
    ]);
    return { health, parcels, vendors, permits, tenants };
  } catch {
    return {
      health: { version: "demo", mode: "interactive_demo" },
      parcels: DEMO_PARCELS,
      vendors: DEMO_VENDORS,
      permits: DEMO_PERMITS,
      tenants: DEMO_TENANTS,
    };
  }
}

export default async function DeskPage() {
  const desk = await loadDesk();

  return (
    <>
      <PageIntro kicker="Operator desk" title="Five agents. One field book.">
        Open a card, keep the pre-filled sample, and run it. Every workflow returns a readable
        result. Nothing leaves this preview.
      </PageIntro>

      <Panel className="mb-8 border-copper/40 bg-[#fff8f1]">
        <div className="grid gap-4 md:grid-cols-[1fr_auto] md:items-start">
          <div className="space-y-3">
            <p className="text-[11px] font-medium uppercase tracking-[0.16em] text-copper">
              Interview walkthrough
            </p>
            <ol className="list-decimal space-y-1 pl-5 text-sm leading-relaxed text-ink-soft">
              <li>
                <Link href="/feasibility" className="text-ink underline decoration-rule underline-offset-2">
                  Site kit
                </Link>
                : keep the Austin parcel → Compile kit → Download demo PDF.
              </li>
              <li>
                <Link href="/triage" className="text-ink underline decoration-rule underline-offset-2">
                  Triage
                </Link>
                : tap Burst pipe → Triage ticket → read the simulated SMS drafts.
              </li>
              <li>
                <Link href="/permits" className="text-ink underline decoration-rule underline-offset-2">
                  Permit pulse
                </Link>
                : Run pulse → inspect the from/to status table.
              </li>
              <li>
                <Link href="/drone" className="text-ink underline decoration-rule underline-offset-2">
                  Drone
                </Link>
                : Fly the comparison → confirm look-ahead is held → Download progress PDF.
              </li>
              <li>
                <Link href="/churn" className="text-ink underline decoration-rule underline-offset-2">
                  Churn
                </Link>
                : Score portfolio → open a renewal draft. No email is sent.
              </li>
            </ol>
          </div>
          <div className="flex flex-col items-start gap-2 md:items-end">
            <p className="font-mono text-[12px] text-sage">5 / 5 workflows ready</p>
            <ResetDemoButton />
          </div>
        </div>
      </Panel>

      <div className="mb-8 grid grid-cols-2 gap-3 md:grid-cols-5">
        <Stat label="Parcels" value={desk.parcels.length} />
        <Stat label="Vendors" value={desk.vendors.length} />
        <Stat label="Permits" value={desk.permits.length} />
        <Stat label="Leases" value={desk.tenants.length} />
        <Stat label="Runtime" value={desk.health.version ?? "demo"} tone="sage" />
      </div>

      <div className="mb-8 grid gap-4 md:grid-cols-2">
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
              <p className="mt-3 text-[12px] text-copper">
                Sample: {agent.sample} · {agent.action}
              </p>
            </Panel>
          </Link>
        ))}
      </div>

      <SafetyNote>
        This hosted preview does not send email or SMS, create PandaDoc signatures, write Airtable
        or Notion records, or dispatch a real vendor. Feasibility PDFs are decision-support, not a
        PE stamp, survey, or appraisal.
      </SafetyNote>
    </>
  );
}
