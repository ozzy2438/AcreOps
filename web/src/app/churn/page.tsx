import { PageIntro } from "@/components/ui";
import { ChurnForm } from "./form";

export default function ChurnPage() {
  return (
    <>
      <PageIntro kicker="05  ·  Churn" title="Don’t guess the concession.">
        Sample leases are scored on payment, maintenance, rent-to-market, and building move-outs.
        The offer matches the driver — not a blanket discount — and is never emailed from this demo.
      </PageIntro>
      <ChurnForm />
    </>
  );
}
