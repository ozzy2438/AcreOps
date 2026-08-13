.PHONY: api ui ui-demo test lint evals train-churn demo seed web-smoke

api:
	uvicorn acreops.api.main:app --reload --port 8000

ui:
	cd web && npm install && ACREOPS_API_URL=http://127.0.0.1:8000 npm run dev

ui-demo:
	cd web && npm install && npm run dev

test:
	pytest --cov=acreops --cov-branch --cov-report=term-missing

lint:
	ruff check src tests && mypy src

train-churn:
	python -m acreops.agents.churn.train

seed:
	python -m acreops.demo.seed

evals:
	python evals/run_evals.py --gate --output artifacts/agent-eval.json

demo:
	./scripts/demo.sh

web-smoke:
	cd web && npm run smoke
