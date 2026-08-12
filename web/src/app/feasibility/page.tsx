import { FeasibilityForm } from "./form";
import { PageIntro } from "@/components/ui";
import type { Parcel } from "@/lib/types";

const API = process.env.ACREOPS_API_URL ?? "http://127.0.0.1:8000";

async function loadParcels(): Promise<Parcel[]> {
  try {
    return await fetch(`${API}/catalog/parcels`, { cache: "no-store" }).then((r) => r.json());
  } catch {
    return [];
  }
}

export default async function FeasibilityPage() {
  const parcels = await loadParcels();

  return (
    <>
      <PageIntro kicker="01  ·  Site kit" title="Address in. Packet out.">
        Zoning envelope, sale comps, and a 1-mile demographic ring compile into a branded PDF
        and a PandaDoc draft. Decision-support — not a PE stamp.
      </PageIntro>
      <FeasibilityForm parcels={parcels} />
    </>
  );
}
