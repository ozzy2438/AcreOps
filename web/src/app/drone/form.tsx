"use client";

import { useState } from "react";
import { ArtifactLink } from "@/components/artifact-link";
import { api } from "@/lib/api";
import type { AgentRun } from "@/lib/types";
import { Audit, Button, ErrorNote, Panel, Pill, SafetyNote, Stat, Table } from "@/components/ui";

type Element = {
  name: string;
  planned_pct: number;
  observed_pct: number;
  delta_pct: number;
  status: string;
  confidence: number;
};

type Flag = {
  name: string;
  severity: string;
  kind: string;
  recommended_action: string;
};

type Report = {
  project_name: string;
  overall_planned_pct: number;
  overall_observed_pct: number;
  schedule_delta_days: number;
  narrative: string;
  elements: Element[];
  discrepancies: Flag[];
  superintendent_validated: boolean;
  schedule_updated: boolean;
  pdf_path?: string;
};

function bar(pct: number, tone: "planned" | "observed") {
  const color = tone === "planned" ? "bg-ink/25" : "bg-copper";
  return (
    <div className="flex min-w-28 items-center gap-2">
      <div className="h-1.5 w-20 bg-paper-2 sm:w-24">
        <div className={`h-1.5 ${color}`} style={{ width: `${Math.max(4, Math.min(100, pct))}%` }} />
      </div>
      <span className="font-mono text-[12px]">{pct.toFixed(0)}%</span>
    </div>
  );
}

export function DroneForm() {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [run, setRun] = useState<AgentRun<Report> | null>(null);

  function restoreSample() {
    setError(null);
    setRun(null);
  }

  async function onRun() {
    setPending(true);
    setError(null);
    try {
      setRun(
        await api.post<AgentRun<Report>>("/agents/drone", {
          project_name: "East 6th Lofts",
          skip_interrupt: true,
        }),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Drone pass failed");
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="space-y-6">
      <SafetyNote>
        Sample flight: East 6th Lofts. Observations are compared to a 4D BIM envelope. The
        superintendent gate stays closed — the look-ahead is not updated.
      </SafetyNote>
      <div className="flex flex-wrap gap-2">
        <Button onClick={onRun} pending={pending}>
          Fly the comparison
        </Button>
        <Button tone="ghost" onClick={restoreSample}>
          Restore sample
        </Button>
      </div>
      <ErrorNote message={error} />

      {run ? (
        <>
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            <Stat label="Planned" value={`${run.result.overall_planned_pct}%`} />
            <Stat label="Observed" value={`${run.result.overall_observed_pct}%`} tone="copper" />
            <Stat
              label="Schedule Δ"
              value={`${run.result.schedule_delta_days > 0 ? "+" : ""}${run.result.schedule_delta_days}d`}
              tone={run.result.schedule_delta_days < 0 ? "clay" : "sage"}
            />
            <Stat
              label="Look-ahead"
              value={run.result.schedule_updated ? "updated" : "held"}
              tone={run.result.schedule_updated ? "clay" : "sage"}
            />
          </div>
          <Panel>
            <p className="text-sm leading-relaxed text-ink-soft">{run.result.narrative}</p>
          </Panel>
          <Table
            columns={["Element", "Planned", "Observed", "Δ", "Status"]}
            rows={run.result.elements.map((el) => [
              el.name,
              bar(el.planned_pct, "planned"),
              bar(el.observed_pct, "observed"),
              `${el.delta_pct > 0 ? "+" : ""}${el.delta_pct.toFixed(0)} pp`,
              <Pill
                key={el.name}
                tone={el.status === "delayed" ? "clay" : el.status === "occluded" ? "amber" : "sage"}
              >
                {el.status.replaceAll("_", " ")}
              </Pill>,
            ])}
          />
          <div>
            <p className="mb-2 text-[11px] uppercase tracking-[0.14em] text-ink-soft">
              Flagged — superintendent still owns the dates
            </p>
            <Table
              columns={["Element", "Severity", "Kind", "Action"]}
              rows={run.result.discrepancies.map((d) => [
                d.name,
                d.severity,
                d.kind.replaceAll("_", " "),
                d.recommended_action,
              ])}
            />
          </div>
          <SafetyNote>
            Superintendent validated: {String(run.result.superintendent_validated)}. Schedule
            updated: {String(run.result.schedule_updated)}. No construction dates were written.
          </SafetyNote>
          <div className="flex flex-wrap items-center gap-3">
            <ArtifactLink href={run.result.pdf_path}>Download progress PDF</ArtifactLink>
          </div>
          <Audit events={run.audit} />
        </>
      ) : (
        <Panel>
          <p className="text-sm text-ink-soft">
            East 6th Lofts has delayed shear walls and an occluded MEP zone on purpose. The report
            will say so. The schedule will not move.
          </p>
        </Panel>
      )}
    </div>
  );
}
