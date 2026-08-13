"use client";

import type { CSSProperties } from "react";
import Link from "next/link";

const STEPS = [
  {
    href: "/feasibility",
    name: "Site kit",
    detail: "keep the Austin parcel → Compile kit → Download demo PDF.",
  },
  {
    href: "/triage",
    name: "Triage",
    detail: "tap Burst pipe → Triage ticket → read the simulated SMS drafts.",
  },
  {
    href: "/permits",
    name: "Permit pulse",
    detail: "Run pulse → inspect the from/to status table.",
  },
  {
    href: "/drone",
    name: "Drone",
    detail: "Fly the comparison → confirm look-ahead is held → Download progress PDF.",
  },
  {
    href: "/churn",
    name: "Churn",
    detail: "Score portfolio → open a renewal draft. No email is sent.",
  },
] as const;

export function WalkthroughFan() {
  return (
    <ol className="walkthrough-fan">
      {STEPS.map((step, index) => (
        <li
          key={step.href}
          className="walkthrough-fan__leaf"
          style={{ "--delay": `${80 + index * 110}ms` } as CSSProperties}
        >
          <span className="walkthrough-fan__index">{String(index + 1).padStart(2, "0")}</span>
          <p className="walkthrough-fan__copy">
            <Link href={step.href} className="text-ink underline decoration-rule underline-offset-2">
              {step.name}
            </Link>
            : {step.detail}
          </p>
        </li>
      ))}
    </ol>
  );
}
