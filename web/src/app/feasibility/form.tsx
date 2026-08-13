"use client";

import { useMemo, useState } from "react";
import { ArtifactLink } from "@/components/artifact-link";
import { api } from "@/lib/api";
import { SAMPLE_FEASIBILITY } from "@/lib/samples";
import type { AgentRun, Parcel } from "@/lib/types";
import { Audit, Button, ErrorNote, Field, Input, Panel, SafetyNote, Select, Stat, Table } from "@/components/ui";

type Packet = {
  risk_tier: string;
  executive_summary: string;
  pdf_path?: string;
  pandadoc_document_id?: string;
  pandadoc_status?: string;
  ready_to_sign?: boolean;
  zoning: { zone_code: string; zone_name: string; jurisdiction: string; max_far: number };
  scenarios: {
    label: string;
    units: number;
    gsf: number;
    estimated_hard_cost_usd: number;
    noi_year1_usd: number;
    residual_land_value_usd: number;
  }[];
};

export function FeasibilityForm({ parcels }: { parcels: Parcel[] }) {
  const fallback: Parcel[] = parcels.length
    ? parcels
    : [
        {
          parcel_id: "AUS-14-8821",
          address: "1408 East 6th Street",
          city: "Austin",
          state: "TX",
          zip_code: "78702",
          jurisdiction: "City of Austin",
          acres: 1.18,
        },
      ];

  const [parcelId, setParcelId] = useState(fallback[0].parcel_id);
  const [use, setUse] = useState(SAMPLE_FEASIBILITY.use);
  const [price, setPrice] = useState(SAMPLE_FEASIBILITY.price);
  const [signer, setSigner] = useState(SAMPLE_FEASIBILITY.signer);
  const [email, setEmail] = useState(SAMPLE_FEASIBILITY.email);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [run, setRun] = useState<AgentRun<Packet> | null>(null);

  const parcel = useMemo(
    () => fallback.find((p) => p.parcel_id === parcelId) ?? fallback[0],
    [fallback, parcelId],
  );

  function restoreSample() {
    setParcelId(fallback[0].parcel_id);
    setUse(SAMPLE_FEASIBILITY.use);
    setPrice(SAMPLE_FEASIBILITY.price);
    setSigner(SAMPLE_FEASIBILITY.signer);
    setEmail(SAMPLE_FEASIBILITY.email);
    setError(null);
    setRun(null);
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setPending(true);
    setError(null);
    try {
      const result = await api.post<AgentRun<Packet>>("/agents/feasibility", {
        address: parcel.address,
        city: parcel.city,
        state: parcel.state,
        zip_code: parcel.zip_code,
        parcel_id: parcel.parcel_id,
        intended_use: use,
        land_price_usd: Number(price),
        signer_name: signer,
        signer_email: email,
        broker_name: "AcreOps Broker Desk",
        broker_email: "broker@acreops.local",
      });
      setRun(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Feasibility run failed");
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
      <Panel>
        <form onSubmit={onSubmit} className="space-y-4">
          <SafetyNote>
            Sample parcels are pre-loaded. The PDF is decision-support only — not a PE stamp,
            survey, or appraisal. PandaDoc stays a simulated draft.
          </SafetyNote>
          <Field label="Parcel">
            <Select value={parcelId} onChange={(e) => setParcelId(e.target.value)}>
              {fallback.map((p) => (
                <option key={p.parcel_id} value={p.parcel_id}>
                  {p.address}, {p.city}
                </option>
              ))}
            </Select>
          </Field>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Field label="Intended use">
              <Select value={use} onChange={(e) => setUse(e.target.value)}>
                {"multifamily mixed_use office retail industrial".split(" ").map((v) => (
                  <option key={v} value={v}>
                    {v.replace("_", " ")}
                  </option>
                ))}
              </Select>
            </Field>
            <Field label="Ask / land price">
              <Input value={price} onChange={(e) => setPrice(e.target.value)} inputMode="numeric" />
            </Field>
          </div>
          <Field label="Counterparty">
            <Input value={signer} onChange={(e) => setSigner(e.target.value)} />
          </Field>
          <Field label="Signer email">
            <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          </Field>
          <div className="flex flex-wrap gap-2">
            <Button type="submit" pending={pending}>
              Compile kit
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
          <div className="grid grid-cols-2 gap-3">
            <Stat label="Risk" value={run.result.risk_tier} tone={run.result.risk_tier === "low" ? "sage" : "amber"} />
            <Stat label="Zone" value={run.result.zoning.zone_code} />
            <Stat label="By-right units" value={run.result.scenarios[0]?.units ?? "—"} />
            <Stat label="PandaDoc" value={run.result.pandadoc_document_id ?? "draft"} tone="copper" />
          </div>
          <Panel>
            <p className="text-sm leading-relaxed text-ink-soft">{run.result.executive_summary}</p>
          </Panel>
          <Table
            columns={["Scenario", "Units", "GSF", "Hard cost", "NOI", "Residual"]}
            rows={run.result.scenarios.map((s) => [
              s.label,
              s.units,
              Math.round(s.gsf).toLocaleString(),
              `$${Math.round(s.estimated_hard_cost_usd).toLocaleString()}`,
              `$${Math.round(s.noi_year1_usd).toLocaleString()}`,
              `$${Math.round(s.residual_land_value_usd).toLocaleString()}`,
            ])}
          />
          <SafetyNote>
            PandaDoc status is {run.result.pandadoc_status ?? "demo_draft"}. Nothing was sent for
            signature and ready-to-sign stays {String(Boolean(run.result.ready_to_sign))}.
          </SafetyNote>
          <div className="flex flex-wrap items-center gap-3">
            <ArtifactLink href={run.result.pdf_path}>Download demo PDF</ArtifactLink>
          </div>
          <Audit events={run.audit} />
        </div>
      ) : (
        <Panel>
          <p className="text-sm text-ink-soft">
            Keep the Austin sample and compile. The agent walks zoning → comps → demographics →
            underwrite → packet, then offers a downloadable demo PDF.
          </p>
        </Panel>
      )}
    </div>
  );
}
