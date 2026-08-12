from __future__ import annotations

import argparse
import json
from pathlib import Path

from acreops.agents.churn.features import FEATURE_COLUMNS, feature_frame
from acreops.agents.churn.graph import load_leases
from acreops.agents.drone.vision import estimate_progress, flag_discrepancies, load_bim
from acreops.agents.permits.portal import _LAST_SEEN, detect_changes, scrape_portal, watched_permits
from acreops.agents.triage.classifier import classify_ticket
from acreops.schemas.triage import TicketIntake


def _intake(text: str) -> TicketIntake:
    return TicketIntake(
        tenant_name="Eval",
        unit_id="1",
        property_id="harbor-lofts",
        address="x",
        description=text,
    )


def run() -> dict:
    cases = []

    gold = [
        ("burst pipe flooding the unit", "emergency", "plumbing"),
        ("no heat and it is freezing", "emergency", "hvac"),
        ("need a light bulb replaced", "tenant_responsibility", "general"),
        ("dishwasher is not draining", "urgent", "appliance"),
        ("squeaky bedroom door", "routine", "general"),
    ]
    triage_ok = 0
    for text, sev, trade in gold:
        clf = classify_ticket(_intake(text))
        hit = clf.severity.value == sev and (clf.trade.value == trade or trade == "general")
        triage_ok += int(hit)
        cases.append({"id": f"triage:{sev}", "pass": hit})
    triage_acc = triage_ok / len(gold)

    _LAST_SEEN.clear()
    records = watched_permits()
    snaps = [scrape_portal(r, force_change=True) for r in records]
    changes = detect_changes(records, snaps)
    permit_ok = len(changes) == len(records)
    cases.append({"id": "permits:force_change_all", "pass": permit_ok})

    _, elements, observations = load_bim("East 6th Lofts")
    estimates = estimate_progress(elements, observations)
    flags = flag_discrepancies(estimates)
    kinds = {f.kind for f in flags}
    drone_ok = {"behind_schedule", "occlusion"}.issubset(kinds)
    cases.append({"id": "drone:flag_kinds", "pass": drone_ok})

    frame = feature_frame(load_leases())
    churn_ok = list(frame.columns[1:]) == FEATURE_COLUMNS and len(frame) >= 5
    cases.append({"id": "churn:feature_frame", "pass": churn_ok})

    gates = {
        "triage_accuracy": triage_acc,
        "permit_diff": 1.0 if permit_ok else 0.0,
        "drone_flags": 1.0 if drone_ok else 0.0,
        "churn_features": 1.0 if churn_ok else 0.0,
    }
    thresholds = {
        "triage_accuracy": 0.8,
        "permit_diff": 1.0,
        "drone_flags": 1.0,
        "churn_features": 1.0,
    }
    passed = all(gates[k] >= thresholds[k] for k in thresholds)
    return {"passed": passed, "gates": gates, "thresholds": thresholds, "cases": cases}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="store_true")
    parser.add_argument("--output", default="artifacts/agent-eval.json")
    args = parser.parse_args()
    report = run()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["gates"], indent=2))
    if args.gate and not report["passed"]:
        print("EVAL GATE FAILED")
        return 1
    print("EVAL GATE PASSED" if report["passed"] else "eval complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
