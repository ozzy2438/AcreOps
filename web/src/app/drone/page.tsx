import { PageIntro } from "@/components/ui";
import { DroneForm } from "./form";

export default function DronePage() {
  return (
    <>
      <PageIntro kicker="04  ·  Drone" title="Photos do not move the look-ahead.">
        Vision occupancy is compared to the 4D BIM envelope. Occlusions and slips are flagged.
        A superintendent still has to say yes before any date changes.
      </PageIntro>
      <DroneForm />
    </>
  );
}
