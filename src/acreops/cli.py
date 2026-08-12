from __future__ import annotations

import argparse
import json

from acreops.agents.churn.graph import run_churn_sweep
from acreops.agents.drone.graph import run_drone_progress
from acreops.agents.feasibility.graph import run_feasibility
from acreops.agents.permits.graph import run_permit_pulse
from acreops.agents.triage.graph import run_triage


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="acreops", description="AcreOps agent runner")
    sub = parser.add_subparsers(dest="cmd", required=True)

    feas = sub.add_parser("feasibility", help="Run site feasibility kit")
    feas.add_argument("--address", default="1408 East 6th Street")
    feas.add_argument("--city", default="Austin")
    feas.add_argument("--state", default="TX")
    feas.add_argument("--zip", dest="zip_code", default="78702")
    feas.add_argument("--use", dest="intended_use", default="multifamily")

    triage = sub.add_parser("triage", help="Triage a maintenance ticket")
    triage.add_argument("--description", required=True)
    triage.add_argument("--tenant", default="Alex Rivera")
    triage.add_argument("--unit", default="4B")
    triage.add_argument("--property", default="harbor-lofts")
    triage.add_argument("--address", default="88 Harbor Way")
    triage.add_argument("--phone", default="+15125550001")

    pulse = sub.add_parser("permits", help="Poll permit portals")
    pulse.add_argument("--no-force", action="store_true")

    drone = sub.add_parser("drone", help="Run drone vs BIM progress")
    drone.add_argument("--project", default="East 6th Lofts")

    churn = sub.add_parser("churn", help="Score lease churn and draft offers")
    churn.add_argument("--horizon", type=int, default=90)

    args = parser.parse_args(argv)
    if args.cmd == "feasibility":
        run = run_feasibility(
            {
                "address": args.address,
                "city": args.city,
                "state": args.state,
                "zip_code": args.zip_code,
                "intended_use": args.intended_use,
                "signer_name": "Jordan Hale",
                "signer_email": "jordan.hale@lp.example",
            }
        )
    elif args.cmd == "triage":
        run = run_triage(
            {
                "tenant_name": args.tenant,
                "tenant_phone": args.phone,
                "unit_id": args.unit,
                "property_id": args.property,
                "address": args.address,
                "description": args.description,
            }
        )
    elif args.cmd == "permits":
        run = run_permit_pulse(force_change=not args.no_force)
    elif args.cmd == "drone":
        run = run_drone_progress(project_name=args.project, skip_interrupt=True)
    else:
        run = run_churn_sweep(horizon_days=args.horizon)
    print(json.dumps(run.model_dump(mode="json"), indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
