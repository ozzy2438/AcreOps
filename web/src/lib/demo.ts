type Json = Record<string, unknown>;

export const DEMO_PARCELS = [
  {
    parcel_id: "AUS-14-8821",
    address: "1408 East 6th Street",
    city: "Austin",
    state: "TX",
    zip_code: "78702",
    jurisdiction: "City of Austin",
    acres: 1.18,
    zone_code: "CS-MU-V-CO-NP",
    zone_name: "Commercial Services / Mixed Use Vertical",
    max_far: 2,
    max_density: 54,
    risk: "medium",
  },
  {
    parcel_id: "CLT-07-4410",
    address: "512 West Morehead Street",
    city: "Charlotte",
    state: "NC",
    zip_code: "28202",
    jurisdiction: "City of Charlotte",
    acres: 1.42,
    zone_code: "UMUD",
    zone_name: "Uptown Mixed Use District",
    max_far: 6,
    max_density: 120,
    risk: "low",
  },
  {
    parcel_id: "DEN-22-1904",
    address: "2550 Walnut Street",
    city: "Denver",
    state: "CO",
    zip_code: "80205",
    jurisdiction: "City and County of Denver",
    acres: 0.86,
    zone_code: "C-MX-8",
    zone_name: "Urban Center Mixed Use 8",
    max_far: 5,
    max_density: 100,
    risk: "high",
  },
];

export const DEMO_VENDORS = [
  { vendor_id: "DEMO-PLM-01", name: "Demo Plumbing Team", trade: "plumbing", zone: "central", rating: 4.8, emergency_available: true },
  { vendor_id: "DEMO-HVAC-01", name: "Demo HVAC Team", trade: "hvac", zone: "all", rating: 4.7, emergency_available: true },
  { vendor_id: "DEMO-ELC-01", name: "Demo Electrical Team", trade: "electrical", zone: "central", rating: 4.9, emergency_available: true },
  { vendor_id: "DEMO-APL-01", name: "Demo Appliance Team", trade: "appliance", zone: "south", rating: 4.4, emergency_available: false },
  { vendor_id: "DEMO-LCK-01", name: "Demo Locksmith Team", trade: "locksmith", zone: "all", rating: 4.5, emergency_available: true },
  { vendor_id: "DEMO-PST-01", name: "Demo Pest Team", trade: "pest", zone: "north", rating: 4.3, emergency_available: false },
  { vendor_id: "DEMO-GEN-01", name: "Demo General Team", trade: "general", zone: "south", rating: 4.2, emergency_available: false },
  { vendor_id: "DEMO-PLM-02", name: "Demo Plumbing Backup", trade: "plumbing", zone: "north", rating: 4.6, emergency_available: true },
];

export const DEMO_PERMITS = [
  { permit_number: "BP-2026-18442", project_name: "East 6th Lofts", address: "1408 East 6th Street, Austin, TX", jurisdiction: "City of Austin Development Services", permit_type: "Commercial building", current_status: "under_review", notes: "Structural comments expected." },
  { permit_number: "SP-2026-0771", project_name: "East 6th Lofts site plan", address: "1408 East 6th Street, Austin, TX", jurisdiction: "City of Austin Development Services", permit_type: "Site plan", current_status: "corrections_required", notes: "Additional detention calculation requested." },
  { permit_number: "BLD-26-44190", project_name: "Morehead Tower", address: "512 West Morehead Street, Charlotte, NC", jurisdiction: "Mecklenburg County LUESA", permit_type: "High-rise building", current_status: "issued", notes: "Foundation inspection window opening." },
  { permit_number: "LOG-2026-3301", project_name: "Walnut Flats", address: "2550 Walnut Street, Denver, CO", jurisdiction: "Denver Development Services", permit_type: "Log plan", current_status: "submitted", notes: "Awaiting completeness." },
];

export const DEMO_TENANTS = [
  { tenant_id: "DEMO-T1", tenant_name: "Resident A", property_name: "Sample Property", unit_id: "D-01", monthly_rent: 2140, lease_end: "2026-09-30" },
  { tenant_id: "DEMO-T2", tenant_name: "Resident B", property_name: "Sample Property", unit_id: "D-02", monthly_rent: 1675, lease_end: "2026-10-14" },
  { tenant_id: "DEMO-T3", tenant_name: "Resident C", property_name: "Sample Property", unit_id: "D-03", monthly_rent: 1890, lease_end: "2026-08-31" },
  { tenant_id: "DEMO-T4", tenant_name: "Resident D", property_name: "Sample Property", unit_id: "D-04", monthly_rent: 2410, lease_end: "2026-09-15" },
  { tenant_id: "DEMO-T5", tenant_name: "Resident E", property_name: "Sample Property", unit_id: "D-05", monthly_rent: 2050, lease_end: "2026-10-31" },
];

const vendorBook: Record<string, { name: string; phone: string; avg_response_min: number }> = {
  plumbing: { name: "Demo Plumbing Team", phone: "demo-contact", avg_response_min: 38 },
  hvac: { name: "Demo HVAC Team", phone: "demo-contact", avg_response_min: 52 },
  electrical: { name: "Demo Electrical Team", phone: "demo-contact", avg_response_min: 40 },
  appliance: { name: "Demo Appliance Team", phone: "demo-contact", avg_response_min: 90 },
  locksmith: { name: "Demo Locksmith Team", phone: "demo-contact", avg_response_min: 28 },
  pest: { name: "Demo Pest Team", phone: "demo-contact", avg_response_min: 240 },
  general: { name: "Demo General Team", phone: "demo-contact", avg_response_min: 180 },
};

const now = () => new Date().toISOString();
const runId = (agent: string) => `demo-${agent}-${Date.now().toString(36)}`;
const audit = (agent: string, actions: string[]) =>
  actions.map((action) => ({ agent, action, timestamp: now(), actor: "demo_agent", payload: {} }));

function agentRun(agent: string, result: Json, actions: string[]) {
  return {
    run_id: runId(agent),
    agent,
    status: "completed",
    started_at: now(),
    finished_at: now(),
    result,
    audit: audit(agent, actions),
    demo: true,
  };
}

function feasibility(body: Json) {
  const parcel =
    DEMO_PARCELS.find((item) => item.parcel_id === body.parcel_id) ?? DEMO_PARCELS[0];
  const baseUnits = Math.max(8, Math.round(parcel.acres * parcel.max_density));
  const price = Number(body.land_price_usd ?? 0);
  const makeScenario = (label: string, multiplier: number, costMultiplier: number) => {
    const units = Math.round(baseUnits * multiplier);
    const gsf = Math.round(units * 850 * 1.18);
    const hardCost = Math.round(gsf * 265 * costMultiplier);
    const noi = Math.round(units * 850 * 2.85 * 12 * 0.62 * multiplier);
    return {
      label,
      units,
      gsf,
      estimated_hard_cost_usd: hardCost,
      noi_year1_usd: noi,
      residual_land_value_usd: Math.round(noi / 0.055 - hardCost * 1.22),
    };
  };
  const scenarios = [
    makeScenario("By-right", 1, 1),
    makeScenario("Density bonus / inclusionary", 1.2, 1.06),
    makeScenario("Conservative absorption", 0.75, 0.98),
  ];
  const risk = price && scenarios[0].residual_land_value_usd < price ? "high" : parcel.risk;
  const result = {
    risk_tier: risk,
    executive_summary: `${parcel.address}, ${parcel.city} is zoned ${parcel.zone_code} (${parcel.zone_name}). The demo by-right envelope supports ${scenarios[0].units} units at ${parcel.max_far} FAR. Composite site risk is ${risk}. Validate all source records with qualified professionals before a transaction.`,
    pdf_path: "/artifacts/feasibility-demo.pdf",
    pandadoc_document_id: "DEMO-PD-18442",
    pandadoc_status: "demo_draft",
    ready_to_sign: false,
    zoning: {
      zone_code: parcel.zone_code,
      zone_name: parcel.zone_name,
      jurisdiction: parcel.jurisdiction,
      max_far: parcel.max_far,
    },
    scenarios,
  };
  return agentRun("site_feasibility", result, [
    "compile_zoning",
    "compile_comps",
    "compile_demographics",
    "underwrite",
    "assemble_demo_packet",
  ]);
}

function classify(text: string) {
  const value = text.toLowerCase();
  const emergency = /flood|burst pipe|gas smell|no heat|sparking|smoke|fire|exposed wire/.test(value);
  const tenant = /light ?bulb|air filter|lockout|lost (my )?key/.test(value);
  const urgent = /no hot water|no ac|a\/c|dishwasher|not draining|leak|pest|roach|mice/.test(value);
  const severity = emergency ? "emergency" : tenant ? "tenant_responsibility" : urgent ? "urgent" : "routine";
  const trade = /dishwasher|fridge|washer|dryer|stove|oven/.test(value)
    ? "appliance"
    : /lock|key/.test(value)
      ? "locksmith"
      : /pest|roach|mice|rat|bug/.test(value)
        ? "pest"
        : /pipe|leak|drain|toilet|sewage|faucet|water/.test(value)
          ? "plumbing"
          : /heat|hvac|ac\b|a\/c|furnace/.test(value)
            ? "hvac"
            : /electric|outlet|breaker|spark|wire|power/.test(value)
              ? "electrical"
              : "general";
  return { severity, trade, tenant };
}

function triage(body: Json) {
  const description = String(body.description ?? "");
  const tenantName = String(body.tenant_name ?? "Resident");
  const unit = String(body.unit_id ?? "—");
  const { severity, trade, tenant } = classify(description);
  const sla = { emergency: 2, urgent: 8, routine: 48, tenant_responsibility: 120 }[severity];
  const vendor = tenant ? null : { ...vendorBook[trade], trade };
  const workOrder = `DEMO-WO-${Math.abs(description.length * 97 + unit.length * 13)}`;
  const status = tenant ? "complete" : vendor ? "dispatched" : "needs_human";
  const tenantSms = tenant
    ? `Hi ${tenantName.split(" ")[0]}, this looks like a tenant-responsibility item. No message was sent. Demo ref ${workOrder}.`
    : `${severity.toUpperCase()} ${trade} ticket ${workOrder}. ${vendor?.name ?? "A manager"} is the simulated assignee. No SMS was sent.`;
  const vendorSms = vendor
    ? `DEMO ONLY — ${severity.toUpperCase()} ${workOrder}: unit ${unit}. ${description.slice(0, 120)}`
    : undefined;
  return agentRun(
    "tenant_triage",
    {
      work_order_id: workOrder,
      status,
      tenant_sms: tenantSms,
      vendor_sms: vendorSms,
      classification: {
        severity,
        trade,
        sla_hours: sla,
        reasoning: `Deterministic demo rules classified this request as ${severity}/${trade}. No external system was updated.`,
        recommended_action: tenant ? "reply_self_help" : `dispatch_${severity}_vendor`,
      },
      vendor,
    },
    ["classify", "assign_vendor", "queue_demo_notifications"],
  );
}

function permits(body: Json) {
  const force = body.force_change !== false;
  const next: Record<string, string> = {
    submitted: "under_review",
    under_review: "corrections_required",
    corrections_required: "approved",
    approved: "issued",
    issued: "inspection_scheduled",
  };
  const snapshots = DEMO_PERMITS.map((permit) => ({
    permit_number: permit.permit_number,
    status: force ? next[permit.current_status] ?? permit.current_status : permit.current_status,
    status_text: (force ? next[permit.current_status] ?? permit.current_status : permit.current_status).replaceAll("_", " "),
  }));
  const changes = force
    ? DEMO_PERMITS.map((permit, index) => ({
        permit_number: permit.permit_number,
        project_name: permit.project_name,
        old_status: permit.current_status,
        new_status: snapshots[index].status,
        action_required: ["corrections_required", "approved"].includes(snapshots[index].status),
        action_summary: `Demo status moved to ${snapshots[index].status.replaceAll("_", " ")}. Review the city portal before acting.`,
        email_sent: false,
        notion_updated: false,
      }))
    : [];
  return agentRun(
    "permit_pulse",
    { snapshots, changes, notifications: [], timeline: [] },
    ["poll_demo_portals", "detect_changes", "prepare_demo_notifications"],
  );
}

const droneElements = [
  { name: "Level 2 podium slab", planned_pct: 100, observed_pct: 100, delta_pct: 0, status: "complete", confidence: 0.93 },
  { name: "Level 3 shear walls", planned_pct: 80, observed_pct: 52, delta_pct: -28, status: "delayed", confidence: 0.81 },
  { name: "Level 4 metal deck", planned_pct: 45, observed_pct: 18, delta_pct: -27, status: "delayed", confidence: 0.77 },
  { name: "Level 1 MEP rough-in", planned_pct: 35, observed_pct: 30, delta_pct: -5, status: "occluded", confidence: 0.58 },
  { name: "Alley paving and utility lids", planned_pct: 20, observed_pct: 38, delta_pct: 18, status: "ahead", confidence: 0.86 },
];

function drone() {
  const discrepancies = [
    { name: "Level 3 shear walls", severity: "critical", kind: "behind_schedule", recommended_action: "Confirm crew and material constraints before changing dates." },
    { name: "Level 4 metal deck", severity: "critical", kind: "behind_schedule", recommended_action: "Validate the deck quantity during the next field walk." },
    { name: "Level 1 MEP rough-in", severity: "watch", kind: "occlusion", recommended_action: "Re-fly or walk this zone; do not update the schedule." },
    { name: "Alley paving and utility lids", severity: "info", kind: "ahead_of_schedule", recommended_action: "Confirm quality hold-points before pulling successors forward." },
  ];
  return agentRun(
    "drone_progress",
    {
      project_name: "East 6th Lofts",
      overall_planned_pct: 56,
      overall_observed_pct: 47.6,
      schedule_delta_days: -1,
      narrative: "Demo comparison: observed progress is 47.6% versus 56.0% planned. Two delayed elements and one occluded zone require superintendent review. No schedule was updated.",
      elements: droneElements,
      discrepancies,
      superintendent_validated: false,
      schedule_updated: false,
      pdf_path: "/artifacts/drone-progress-demo.pdf",
    },
    ["compare_demo_observations_to_bim", "hold_for_superintendent", "render_demo_report"],
  );
}

const churnPredictions = [
  { tenant_id: "DEMO-T1", tenant_name: "Resident A", property_name: "Sample Property", unit_id: "D-01", days_to_expiry: 79, churn_probability: 0.82, risk_tier: "critical", primary_driver: "maintenance", recommended_incentive: "Priority maintenance + $150 amenity credit", incentive_budget: 150 },
  { tenant_id: "DEMO-T2", tenant_name: "Resident B", property_name: "Sample Property", unit_id: "D-02", days_to_expiry: 48, churn_probability: 0.74, risk_tier: "critical", primary_driver: "maintenance", recommended_incentive: "Priority maintenance + $150 amenity credit", incentive_budget: 150 },
  { tenant_id: "DEMO-T3", tenant_name: "Resident C", property_name: "Sample Property", unit_id: "D-03", days_to_expiry: 18, churn_probability: 0.58, risk_tier: "high", primary_driver: "market", recommended_incentive: "Match nearby special with a $400 renewal gift", incentive_budget: 400 },
  { tenant_id: "DEMO-T4", tenant_name: "Resident D", property_name: "Sample Property", unit_id: "D-04", days_to_expiry: 62, churn_probability: 0.31, risk_tier: "low", primary_driver: "unknown", recommended_incentive: "Standard renewal + $50 gift card", incentive_budget: 50 },
];

function churn(body: Json) {
  const horizon = Number(body.horizon_days ?? 90);
  const floor = Number(body.min_probability ?? 0.35);
  const predictions = churnPredictions.filter(
    (item) => item.days_to_expiry <= horizon && item.churn_probability >= floor,
  );
  const offers = predictions.map((item) => ({
    tenant_id: item.tenant_id,
    subject: `Demo renewal draft — ${item.property_name} ${item.unit_id}`,
    body: `Hi ${item.tenant_name.split(" ")[0]},\n\nThis is a DEMO renewal draft. Suggested offer: ${item.recommended_incentive}.\n\nNo email was sent and no financial commitment was created. A manager must review the data, fairness checks, and final terms.`,
    incentive_value_usd: item.incentive_budget,
    email_sent: false,
  }));
  return agentRun(
    "lease_churn",
    { predictions, offers, emails: [] },
    ["score_demo_portfolio", "draft_demo_offers", "hold_for_manager_review"],
  );
}

export function handleDemo(path: string, method: string, body: Json = {}) {
  if (method === "GET" && path === "health") {
    return { ok: true, service: "acreops-web-demo", version: "0.2.0-preview", mode: "interactive_demo" };
  }
  if (method === "GET" && path === "catalog/parcels") return DEMO_PARCELS;
  if (method === "GET" && path === "catalog/vendors") return DEMO_VENDORS;
  if (method === "GET" && path === "catalog/permits") return DEMO_PERMITS;
  if (method === "GET" && path === "catalog/tenants") return DEMO_TENANTS;
  if (method === "GET" && path === "catalog/bim") return [{ project_name: "East 6th Lofts", elements: droneElements }];
  if (method === "POST" && path === "agents/feasibility") return feasibility(body);
  if (method === "POST" && (path === "agents/triage" || path === "webhooks/appfolio")) return triage(body);
  if (method === "POST" && path === "agents/permits") return permits(body);
  if (method === "POST" && path === "agents/drone") return drone();
  if (method === "POST" && path === "agents/churn") return churn(body);
  return null;
}

function pdfEscape(value: string) {
  return value.replaceAll("\\", "\\\\").replaceAll("(", "\\(").replaceAll(")", "\\)");
}

export function demoPdf(kind: string) {
  const isDrone = kind.includes("drone");
  const title = isDrone ? "AcreOps Drone Progress Demo" : "AcreOps Site Feasibility Demo";
  const lines = isDrone
    ? ["East 6th Lofts", "Planned 56.0% / observed 47.6%", "Schedule update: HELD", "Demo only - superintendent review required"]
    : ["1408 East 6th Street, Austin TX", "Zoning, comps, demographics and scenarios compiled", "PandaDoc status: DEMO DRAFT", "Decision support only - validate all sources"];
  const stream = [
    "BT",
    "/F1 20 Tf",
    "72 720 Td",
    `(${pdfEscape(title)}) Tj`,
    "/F1 11 Tf",
    ...lines.flatMap((line) => ["0 -30 Td", `(${pdfEscape(line)}) Tj`]),
    "0 -50 Td",
    "(No external message, signature, schedule, or system update occurred.) Tj",
    "ET",
  ].join("\n");
  const objects = [
    "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj",
    "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj",
    "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj",
    "4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj",
    `5 0 obj << /Length ${new TextEncoder().encode(stream).length} >> stream\n${stream}\nendstream endobj`,
  ];
  let pdf = "%PDF-1.4\n";
  const offsets = [0];
  for (const object of objects) {
    offsets.push(new TextEncoder().encode(pdf).length);
    pdf += `${object}\n`;
  }
  const xref = new TextEncoder().encode(pdf).length;
  pdf += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
  pdf += offsets.slice(1).map((offset) => `${String(offset).padStart(10, "0")} 00000 n \n`).join("");
  pdf += `trailer << /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF`;
  return new TextEncoder().encode(pdf);
}
