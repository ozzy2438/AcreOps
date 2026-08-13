"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { AgentRun, Permit } from "@/lib/types";
import { Audit, Button, ErrorNote, Panel, Pill, Table } from "@/components/ui";

type Change = {
  permit_number: string;
  project_name: string;
  old_status: string;
  new_status: string;
  action_required: boolean;
  action_summary: string;
};

type Pulse = {
  changes: Change[];
  snapshots: { permit_number: string; status: string; status_text: string }[];
};

export function PermitPulse({ watched }: { watched: Permit[] }) {
  const [force, setForce] = useState(true);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [run, setRun] = useState<AgentRun<Pulse> | null>(null);

  async function onRun() {
    setPending(true);
    setError(null);
    try {
      setRun(await api.post<AgentRun<Pulse>>("/agents/permits", { force_change: force }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Pulse failed");
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="space-y-6">
      {watched.length ? (
        <Table
          columns={["Permit", "Project", "Status", "Jurisdiction"]}
          rows={watched.map((p) => [
            <span key={p.permit_number} className="font-mono text-[12px]">
              {p.permit_number}
            </span>,
            p.project_name,
            <Pill key={`${p.permit_number}-s`}>{p.current_status.replaceAll("_", " ")}</Pill>,
            p.jurisdiction,
          ])}
        />
      ) : (
        <Panel>
          <p className="text-sm text-ink-soft">No watched permits loaded. API may be offline.</p>
        </Panel>
      )}

      <div className="flex flex-wrap items-center gap-4">
        <label className="flex items-center gap-2 text-sm text-ink-soft">
          <input type="checkbox" checked={force} onChange={(e) => setForce(e.target.checked)} />
          Simulate a status change on this pass
        </label>
        <Button onClick={onRun} pending={pending}>
          Run pulse
        </Button>
      </div>
      <ErrorNote message={error} />

      {run ? (
        run.result.changes.length ? (
          <div className="space-y-4">
            <Table
              columns={["Permit", "From", "To", "Action"]}
              rows={run.result.changes.map((c) => [
                c.permit_number,
                c.old_status.replaceAll("_", " "),
                c.new_status.replaceAll("_", " "),
                c.action_summary,
              ])}
            />
            <p className="text-sm text-ink-soft">
              Demo notifications prepared. No email was sent and no Notion page was changed.
            </p>
            <Audit events={run.audit} />
          </div>
        ) : (
          <Panel>
            <p className="text-sm text-ink-soft">Quiet night. No status changes this pass.</p>
          </Panel>
        )
      ) : null}
    </div>
  );
}
