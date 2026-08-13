"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { SAMPLE_PROPERTIES, SAMPLE_TRIAGE, TRIAGE_TICKETS } from "@/lib/samples";
import type { AgentRun } from "@/lib/types";
import {
  Audit,
  Button,
  ErrorNote,
  Field,
  Input,
  Panel,
  Pill,
  SafetyNote,
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

export function TriageForm() {
  const [description, setDescription] = useState(SAMPLE_TRIAGE.description);
  const [tenant, setTenant] = useState(SAMPLE_TRIAGE.tenant);
  const [unit, setUnit] = useState(SAMPLE_TRIAGE.unit);
  const [propertyId, setPropertyId] = useState(SAMPLE_TRIAGE.propertyId);
  const [phone, setPhone] = useState(SAMPLE_TRIAGE.phone);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [run, setRun] = useState<AgentRun<WorkOrder> | null>(null);

  function restoreSample() {
    setDescription(SAMPLE_TRIAGE.description);
    setTenant(SAMPLE_TRIAGE.tenant);
    setUnit(SAMPLE_TRIAGE.unit);
    setPropertyId(SAMPLE_TRIAGE.propertyId);
    setPhone(SAMPLE_TRIAGE.phone);
    setError(null);
    setRun(null);
  }

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
          <SafetyNote>
            Tickets are synthetic. Classification and vendor pick run in code. No AppFolio work
            order, Airtable row, or SMS is created.
          </SafetyNote>
          <Field label="Resident description">
            <Textarea value={description} onChange={(e) => setDescription(e.target.value)} />
          </Field>
          <div className="flex flex-wrap gap-2">
            {TRIAGE_TICKETS.map((sample) => (
              <button
                key={sample.label}
                type="button"
                onClick={() => setDescription(sample.text)}
                className="border border-rule px-2 py-1 text-[11px] text-ink-soft hover:border-ink hover:text-ink"
              >
                {sample.label}
              </button>
            ))}
          </div>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Field label="Tenant">
              <Input value={tenant} onChange={(e) => setTenant(e.target.value)} />
            </Field>
            <Field label="Unit">
              <Input value={unit} onChange={(e) => setUnit(e.target.value)} />
            </Field>
            <Field label="Property">
              <Select value={propertyId} onChange={(e) => setPropertyId(e.target.value)}>
                {SAMPLE_PROPERTIES.map((id) => (
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
          <div className="flex flex-wrap gap-2">
            <Button type="submit" pending={pending}>
              Triage ticket
            </Button>
            <Button type="button" tone="ghost" onClick={restoreSample}>
              Restore sample
            </Button>
          </div>
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
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <Pill tone={tone}>{run.result.status}</Pill>
              <span className="font-mono text-[12px] text-ink-soft">{run.result.work_order_id}</span>
            </div>
            <p className="text-sm leading-relaxed text-ink-soft">{run.result.classification.reasoning}</p>
            {run.result.vendor ? (
              <p className="mt-4 text-sm">
                Simulated assignee <span className="font-medium">{run.result.vendor.name}</span> ·{" "}
                {run.result.vendor.phone} · typical {run.result.vendor.avg_response_min} min
              </p>
            ) : null}
          </Panel>
          {run.result.tenant_sms ? (
            <Panel>
              <p className="mb-1 text-[11px] uppercase tracking-[0.14em] text-ink-soft">
                Simulated tenant SMS
              </p>
              <p className="text-sm">{run.result.tenant_sms}</p>
            </Panel>
          ) : null}
          {run.result.vendor_sms ? (
            <Panel>
              <p className="mb-1 text-[11px] uppercase tracking-[0.14em] text-ink-soft">
                Simulated vendor SMS
              </p>
              <p className="text-sm">{run.result.vendor_sms}</p>
            </Panel>
          ) : null}
          <SafetyNote>Twilio / Airtable were not called. These are preview drafts only.</SafetyNote>
          <Audit events={run.audit} />
        </div>
      ) : (
        <Panel>
          <p className="text-sm text-ink-soft">
            Try a burst pipe, a dead heater, a dishwasher, or a light bulb. Life-safety tickets
            should route as emergency; a light bulb should stay tenant-responsibility.
          </p>
        </Panel>
      )}
    </div>
  );
}
