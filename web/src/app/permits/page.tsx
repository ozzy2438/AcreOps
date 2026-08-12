import { PageIntro } from "@/components/ui";
import type { Permit } from "@/lib/types";
import { PermitPulse } from "./form";

const API = process.env.ACREOPS_API_URL ?? "http://127.0.0.1:8000";

async function loadPermits(): Promise<Permit[]> {
  try {
    return await fetch(`${API}/catalog/permits`, { cache: "no-store" }).then((r) => r.json());
  } catch {
    return [];
  }
}

export default async function PermitsPage() {
  const permits = await loadPermits();
  return (
    <>
      <PageIntro kicker="03  ·  Pulse" title="Stop refreshing the portal.">
        The robot hashes the status field, diffs it against last night, emails the PM, and writes a
        Notion timeline row. City portals stay the system of record.
      </PageIntro>
      <PermitPulse watched={permits} />
    </>
  );
}
