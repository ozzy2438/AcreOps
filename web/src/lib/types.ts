export type AgentName =
  | "site_feasibility"
  | "tenant_triage"
  | "permit_pulse"
  | "drone_progress"
  | "lease_churn";

export type AuditEvent = {
  agent: AgentName;
  action: string;
  timestamp: string;
  actor: string;
  payload: Record<string, unknown>;
};

export type AgentRun<T = Record<string, unknown>> = {
  run_id: string;
  agent: AgentName;
  status: string;
  started_at: string;
  finished_at: string | null;
  result: T;
  audit: AuditEvent[];
  demo: boolean;
};

export type Parcel = {
  parcel_id: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  jurisdiction: string;
  acres: number;
};

export type Permit = {
  permit_number: string;
  project_name: string;
  address: string;
  jurisdiction: string;
  permit_type: string;
  current_status: string;
  notes: string;
};

export type Tenant = {
  tenant_id: string;
  tenant_name: string;
  property_name: string;
  unit_id: string;
  monthly_rent: number;
  lease_end: string;
};

export type Vendor = {
  vendor_id: string;
  name: string;
  trade: string;
  zone: string;
  rating: number;
  emergency_available: boolean;
};
