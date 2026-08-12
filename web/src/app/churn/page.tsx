import { PageIntro } from "@/components/ui";
import { ChurnForm } from "./form";

export default function ChurnPage() {
  return (
    <>
      <PageIntro kicker="05  ·  Churn" title="Don’t guess the concession.">
        LightGBM scores a 90-day non-renewal window from payment, maintenance, rent-to-market, and
        building move-outs. The offer matches the driver — not a blanket discount.
      </PageIntro>
      <ChurnForm />
    </>
  );
}
