from __future__ import annotations

from acreops.adapters.catalog import bim_models, parcels, permits, tenants, vendors
from acreops.agents.churn.train import train_churn_model
from acreops.config import get_settings


def main() -> None:
    settings = get_settings()
    settings.acreops_artifact_dir.mkdir(parents=True, exist_ok=True)
    path = train_churn_model()
    print(
        "Seeded AcreOps demo:\n"
        f"  parcels={len(parcels())} vendors={len(vendors())} "
        f"permits={len(permits())} tenants={len(tenants())} "
        f"bim={len(bim_models())}\n"
        f"  churn model → {path}"
    )


if __name__ == "__main__":
    main()
