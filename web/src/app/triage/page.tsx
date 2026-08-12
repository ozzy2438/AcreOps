import { PageIntro } from "@/components/ui";
import { TriageForm } from "./form";

export default function TriagePage() {
  return (
    <>
      <PageIntro kicker="02  ·  Triage" title="Read the ticket. Dispatch the trade.">
        An AppFolio-shaped request hits a rule classifier — emergency, urgent, routine, or
        tenant-responsibility — then the first eligible vendor on the bench. SMS goes both ways.
      </PageIntro>
      <TriageForm />
    </>
  );
}
