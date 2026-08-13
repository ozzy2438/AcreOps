#!/usr/bin/env node

const BASE = process.env.ACREOPS_SMOKE_URL ?? "http://127.0.0.1:3000";

async function request(path, init = {}) {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "content-type": "application/json",
      ...(init.headers ?? {}),
    },
  });
  const text = await res.text();
  return { res, text };
}

async function json(path, init) {
  const { res, text } = await request(path, init);
  if (!res.ok) {
    throw new Error(`${init?.method ?? "GET"} ${path} -> ${res.status} ${text.slice(0, 240)}`);
  }
  return { res, body: JSON.parse(text) };
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function waitForServer() {
  const deadline = Date.now() + 60_000;
  while (Date.now() < deadline) {
    try {
      const { res } = await request("/api/backend/health");
      if (res.ok) return;
    } catch {
      // Server still booting.
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error(`Server at ${BASE} did not become ready`);
}

async function main() {
  await waitForServer();

  const pages = ["/", "/feasibility", "/triage", "/permits", "/drone", "/churn"];
  for (const page of pages) {
    const { res, text } = await request(page);
    assert(res.ok, `${page} returned ${res.status}`);
    assert(text.includes("Simulated demo") || text.includes("AcreOps"), `${page} missing shell`);
    assert(!text.toLowerCase().includes("application error"), `${page} rendered an application error`);
  }

  const health = await json("/api/backend/health");
  assert(health.body.ok === true, "health.ok");
  assert(health.res.headers.get("x-acreops-runtime") === "interactive-demo", "demo runtime header");

  const parcels = await json("/api/backend/catalog/parcels");
  assert(Array.isArray(parcels.body) && parcels.body.length >= 3, "sample parcels");

  const site = await json("/api/backend/agents/feasibility", {
    method: "POST",
    body: JSON.stringify({
      parcel_id: "AUS-14-8821",
      land_price_usd: 4500000,
      intended_use: "multifamily",
    }),
  });
  assert(site.body.result.pdf_path, "feasibility pdf_path");
  assert(site.body.result.scenarios.length === 3, "feasibility scenarios");
  assert(site.body.result.ready_to_sign === false, "feasibility not ready to sign");

  const leak = await json("/api/backend/webhooks/appfolio", {
    method: "POST",
    body: JSON.stringify({
      tenant_name: "Resident A",
      unit_id: "D-01",
      description: "burst pipe flooding the kitchen",
    }),
  });
  assert(leak.body.result.classification.severity === "emergency", "burst pipe is emergency");
  assert(leak.body.result.classification.trade === "plumbing", "burst pipe is plumbing");
  assert(String(leak.body.result.tenant_sms).includes("No SMS was sent"), "triage SMS is simulated");

  const bulb = await json("/api/backend/webhooks/appfolio", {
    method: "POST",
    body: JSON.stringify({
      tenant_name: "Resident A",
      unit_id: "D-01",
      description: "need a new light bulb in the hallway",
    }),
  });
  assert(bulb.body.result.classification.severity === "tenant_responsibility", "light bulb is tenant");

  const pulse = await json("/api/backend/agents/permits", {
    method: "POST",
    body: JSON.stringify({ force_change: true }),
  });
  assert(pulse.body.result.changes.length >= 4, "permit diffs");
  assert(pulse.body.result.changes.every((change) => change.email_sent === false), "no permit email");
  assert(pulse.body.result.changes.every((change) => change.notion_updated === false), "no Notion write");

  const drone = await json("/api/backend/agents/drone", {
    method: "POST",
    body: JSON.stringify({ project_name: "East 6th Lofts", skip_interrupt: true }),
  });
  assert(drone.body.result.schedule_updated === false, "drone schedule held");
  assert(drone.body.result.superintendent_validated === false, "superintendent gate closed");
  assert(drone.body.result.pdf_path, "drone pdf_path");

  const churn = await json("/api/backend/agents/churn", {
    method: "POST",
    body: JSON.stringify({ horizon_days: 90, min_probability: 0.35, send_email: false }),
  });
  assert(churn.body.result.predictions.length >= 1, "churn predictions");
  assert(churn.body.result.offers.every((offer) => offer.email_sent === false), "no churn email");

  const reset = await json("/api/backend/demo/reset", { method: "POST", body: "{}" });
  assert(reset.body.ok === true, "demo reset");

  for (const artifact of ["/api/backend/artifacts/feasibility-demo.pdf", "/api/backend/artifacts/drone-progress-demo.pdf"]) {
    const { res, text } = await request(artifact);
    assert(res.ok, `${artifact} ${res.status}`);
    assert(res.headers.get("content-type")?.includes("pdf"), `${artifact} content-type`);
    assert(text.startsWith("%PDF"), `${artifact} is not a PDF`);
    assert(text.includes("%%EOF"), `${artifact} missing EOF`);
  }

  console.log(`AcreOps demo smoke passed against ${BASE}`);
}

main().catch((err) => {
  console.error(err instanceof Error ? err.message : err);
  process.exit(1);
});
