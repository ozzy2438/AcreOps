#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src
mkdir -p artifacts

echo "== feasibility =="
python -m acreops.cli feasibility --address "1408 East 6th Street" --city Austin --state TX | python -c "import sys,json; r=json.load(sys.stdin); print(r['result']['risk_tier'], r['result']['pdf_path'])"

echo "== triage =="
python -m acreops.cli triage --description "burst pipe flooding the kitchen" | python -c "import sys,json; r=json.load(sys.stdin); print(r['result']['classification']['severity'], r['result']['vendor']['name'])"

echo "== permits =="
python -m acreops.cli permits | python -c "import sys,json; r=json.load(sys.stdin); print(len(r['result']['changes']), 'changes')"

echo "== drone =="
python -m acreops.cli drone | python -c "import sys,json; r=json.load(sys.stdin); print(r['result']['overall_observed_pct'], r['result']['schedule_updated'])"

echo "== churn =="
python -m acreops.cli churn --horizon 120 | python -c "import sys,json; r=json.load(sys.stdin); print(len(r['result']['predictions']), 'at risk')"

echo "AcreOps demo pass complete."
