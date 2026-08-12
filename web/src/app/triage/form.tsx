"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { AgentRun } from "@/lib/types";
import {
  Audit,
  Button,
  ErrorNote,
  Field,
  Input,
  Panel,
  Pill,
  Select,
  Stat,
  Textarea,
} from "@/components/ui";

type WorkOrder = {
  work_order_id: string;
  status: string;
  tenant_sms?: string;
  vendor_sms?: string;
  classification: {
    severity: string;
    trade: string;
    sla_hours: number;
    reasoning: string;
    recommended_action: string;
  };
  vendor?: { name: string; phone: string; trade: string; avg_response_min: number } | null;
};

const SAMPLES = [
  "Kitchen sink is leaking and water is pooling on the floor.",
  "burst pipe flooding the kitchen",
  "no heat and it is freezing",
  "need a new light bulb in the hallway",
  "dishwasher is not draining",
];

export function TriageForm() {
  const [description, setDescription] = useState(SAMPLES[0]);
  const [tenant, setTenant] = useState("Alex Rivera");
  const [unit, setUnit] = useState("4B");
  const [propertyId, setPropertyId] = useState("harbor-lofts");
  const [phone, setPhone] = useState("+15125550001");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [run, setRun] = useState<AgentRun<WorkOrder> | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setPending(true);
    setError(null);
    try {
      const result = await api.post<AgentRun<WorkOrder>>("/webhooks/appfolio", {
        tenant_name: tenant,
        tenant_phone: phone,
        unit_id: unit,
        property_id: propertyId,
        address: `${unit} @ ${propertyId}`,
        description,
      });
      setRun(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Triage failed");
    } finally {
      setPending(false);
    }
  }

  const tone =
    run?.result.classification.severity === "emergency"
      ? "clay"
      : run?.result.classification.severity === "urgent"
        ? "amber"
        : "sage";

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Panel>
        <form onSubmit={onSubmit} className="space-y-4">
          <Field label="Resident description">
            <Textarea value={description} onChange={(e) => setDescription(e.target.value)} />
          </Field>
          <div className="flex flex-wrap gap-2">
            {SAMPLES.map((sample) => (
              <button
                key={sample}
                type="button"
                onClick={() => setDescription(sample)}
                className="border border-rule px-2 py-1 text-[11px] text-ink-soft hover:border-ink hover:text-ink"
              >
                {sample.slice(0, 28)}…
              </button>
            ))}
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Tenant">
              <Input value={tenant} onChange={(e) => setTenant(e.target.value)} />
            </Field>
            <Field label="Unit">
              <Input value={unit} onChange={(e) => setUnit(e.target.value)} />
            </Field>
            <Field label="Property">
              <Select value={propertyId} onChange={(e) => setPropertyId(e.target.value)}>
                {"harbor-lofts oak-ridge cedar-court midtown-flats".split(" ").map((id) => (
                  <option key={id} value={id}>
                    {id}
                  </option>
                ))}
              </Select>
            </Field>
            <Field label="Mobile">
              <Input value={phone} onChange={(e) => setPhone(e.target.value)} />
            </Field>
          </div>
          <Button type="submit" pending={pending}>
            Triage ticket
          </Button>
          <ErrorNote message={error} />
        </form>
      </Panel>

      {run ? (
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-3">
            <Stat label="Severity" value={run.result.classification.severity} tone={tone} />
            <Stat label="Trade" value={run.result.classification.trade} />
            <Stat label="SLA" value={`${run.result.classification.sla_hours}h`} />
          </div>
          <Panel>
            <div className="mb-3 flex items-center gap-2">
              <Pill tone={tone}>{run.result.status}</Pill>
              <span className="font-mono text-[12px] text-ink-soft">{run.result.work_order_id}</span>
            </div>
            <p className="text-sm leading-relaxed text-ink-soft">{run.result.classification.reasoning}</p>
            {run.result.vendor ? (
              <p className="mt-4 text-sm">
                Assigned <span className="font-medium">{run.result.vendor.name}</span> ·{" "}
                {run.result.vendor.phone} · typical {run.result.vendor.avg_response_min} min
              </p>
            ) : null}
          </Panel>
          {run.result.tenant_sms ? (
            <Panel>
              <p className="mb-1 text-[11px] uppercase tracking-[0.14em] text-ink-soft">Tenant SMS</p>
              <p className="text-sm">{run.result.tenant_sms}</p>
            </Panel>
          ) : null}
          {run.result.vendor_sms ? (
            <Panel>
              <p className="mb-1 text-[11px] uppercase tracking-[0.14em] text-ink-soft">Vendor SMS</p>
              <p className="text-sm">{run.result.vendor_sms}</p>
            </Panel>
          ) : null}
          <Audit events={run.audit} />
        </div>
      ) : (
        <Panel>
          <p className="text-sm text-ink-soft">
            Try a burst pipe, a dead heater, a dishwasher, or a light bulb. The classifier should
            not guess life-safety.
          </p>
        </Panel>
      )}
    </div>
  );
}
