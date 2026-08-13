import { PageIntro } from "@/components/ui";
import { DroneForm } from "./form";

export default function DronePage() {
  return (
    <>
      <PageIntro kicker="04  ·  Drone" title="Photos do not move the look-ahead.">
        Sample observations are compared to the 4D BIM envelope. Occlusions and slips are flagged.
        A superintendent still has to say yes before any date changes — this preview keeps the
        look-ahead held.
      </PageIntro>
      <DroneForm />
    </>
  );
}
