"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { AgentRun } from "@/lib/types";
import { Audit, Button, ErrorNote, Field, Panel, Pill, Stat, Table } from "@/components/ui";

type Prediction = {
  tenant_name: string;
  property_name: string;
  unit_id: string;
  days_to_expiry: number;
  churn_probability: number;
  risk_tier: string;
  primary_driver: string;
  recommended_incentive: string;
  incentive_budget: number;
};

type Offer = {
  subject: string;
  body: string;
  tenant_id: string;
  incentive_value_usd: number;
};

type Sweep = {
  predictions: Prediction[];
  offers: Offer[];
};

export function ChurnForm() {
  const [horizon, setHorizon] = useState(90);
  const [floor, setFloor] = useState(0.35);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [run, setRun] = useState<AgentRun<Sweep> | null>(null);
  const [open, setOpen] = useState<string | null>(null);

  async function onRun() {
    setPending(true);
    setError(null);
    try {
      setRun(
        await api.post<AgentRun<Sweep>>("/agents/churn", {
          horizon_days: horizon,
          min_probability: floor,
          send_email: true,
        }),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Churn sweep failed");
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="space-y-6">
      <Panel>
        <div className="grid gap-5 md:grid-cols-[1fr_1fr_auto] md:items-end">
          <Field label={`Horizon · ${horizon} days`}>
            <input
              type="range"
              min={30}
              max={180}
              value={horizon}
              onChange={(e) => setHorizon(Number(e.target.value))}
              className="w-full accent-copper"
            />
          </Field>
          <Field label={`Min probability · ${floor.toFixed(2)}`}>
            <input
              type="range"
              min={0.1}
              max={0.8}
              step={0.05}
              value={floor}
              onChange={(e) => setFloor(Number(e.target.value))}
              className="w-full accent-copper"
            />
          </Field>
          <Button onClick={onRun} pending={pending}>
            Score portfolio
          </Button>
        </div>
        <ErrorNote message={error} />
      </Panel>

      {run ? (
        run.result.predictions.length ? (
          <>
            <div className="grid grid-cols-3 gap-3">
              <Stat label="Flagged" value={run.result.predictions.length} tone="clay" />
              <Stat label="Offers drafted" value={run.result.offers.length} />
              <Stat
                label="Top risk"
                value={`${Math.round(run.result.predictions[0].churn_probability * 100)}%`}
                tone="amber"
              />
            </div>
            <Table
              columns={["Resident", "Home", "Days", "Risk", "Driver", "Offer"]}
              rows={run.result.predictions.map((p) => [
                p.tenant_name,
                `${p.property_name} ${p.unit_id}`,
                p.days_to_expiry,
                <Pill
                  key={p.tenant_name}
                  tone={p.risk_tier === "critical" || p.risk_tier === "high" ? "clay" : "amber"}
                >
                  {Math.round(p.churn_probability * 100)}% {p.risk_tier}
                </Pill>,
                p.primary_driver.replaceAll("_", " "),
                p.recommended_incentive,
              ])}
            />
            <div className="space-y-2">
              {run.result.offers.map((offer) => (
                <Panel key={offer.subject}>
                  <button
                    type="button"
                    className="flex w-full items-center justify-between text-left"
                    onClick={() => setOpen(open === offer.subject ? null : offer.subject)}
                  >
                    <span className="text-sm font-medium">{offer.subject}</span>
                    <span className="font-mono text-[12px] text-copper">
                      ${offer.incentive_value_usd.toFixed(0)}
                    </span>
                  </button>
                  {open === offer.subject ? (
                    <pre className="mt-3 whitespace-pre-wrap font-sans text-sm leading-relaxed text-ink-soft">
                      {offer.body}
                    </pre>
                  ) : null}
                </Panel>
              ))}
            </div>
            <Audit events={run.audit} />
          </>
        ) : (
          <Panel>
            <p className="text-sm text-ink-soft">No tenants above the floor in this window.</p>
          </Panel>
        )
      ) : null}
    </div>
  );
}
