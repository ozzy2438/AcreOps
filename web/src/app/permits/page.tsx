import { PageIntro } from "@/components/ui";
import type { Permit } from "@/lib/types";
import { PermitPulse } from "./form";
import { DEMO_PERMITS } from "@/lib/demo";

const API = process.env.ACREOPS_API_URL;

async function loadPermits(): Promise<Permit[]> {
  if (!API) return DEMO_PERMITS;
  try {
    return await fetch(`${API}/catalog/permits`, { cache: "no-store" }).then((r) => r.json());
  } catch {
    return DEMO_PERMITS;
  }
}

export default async function PermitsPage() {
  const permits = await loadPermits();
  return (
    <>
      <PageIntro kicker="03  ·  Pulse" title="Stop refreshing the portal.">
        The robot hashes the status field and diffs it against last night. Email and Notion drafts
        are prepared in-memory. City portals stay the system of record; nothing is written back.
      </PageIntro>
      <PermitPulse watched={permits} />
    </>
  );
}
