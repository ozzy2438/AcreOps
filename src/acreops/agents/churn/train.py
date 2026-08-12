from __future__ import annotations

from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd

from acreops.agents.churn.features import FEATURE_COLUMNS
from acreops.config import get_settings


def _synthetic_training_frame(n: int = 800, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    late = rng.beta(1.4, 6.0, n)
    maint = rng.gamma(2.2, 2.0, n)
    unresolved = rng.poisson(0.4, n)
    csat = np.clip(rng.normal(3.8, 0.8, n), 1, 5)
    rent_to_market = np.clip(rng.normal(0.97, 0.08, n), 0.75, 1.25)
    vacancy = np.clip(rng.normal(0.05, 0.02, n), 0.01, 0.16)
    moveouts = rng.poisson(0.7, n)
    increase = np.clip(rng.normal(0.035, 0.02, n), 0.0, 0.12)
    tenure = rng.integers(4, 60, n)
    prior = np.clip(tenure // 12 - 1, 0, 6)
    days = rng.integers(15, 140, n)
    logins = rng.integers(0, 12, n)
    auto = rng.integers(0, 2, n)
    nsf = rng.poisson(0.2, n)
    open_wo = rng.poisson(0.6, n)
    rent = rng.normal(1850, 420, n)

    # Latent churn score — matches the product story, not a random label.
    logit = (
        -1.6
        + 3.4 * late
        + 0.12 * maint
        + 0.55 * unresolved
        + -0.55 * (csat - 3.0)
        + 2.4 * np.clip(rent_to_market - 1.0, 0, None)
        + 4.0 * vacancy
        + 0.28 * moveouts
        + 6.0 * increase
        + -0.03 * tenure
        + -0.35 * prior
        + -0.06 * logins
        + -0.25 * auto
        + 0.4 * nsf
    )
    prob = 1 / (1 + np.exp(-logit))
    y = (rng.random(n) < prob).astype(int)

    frame = pd.DataFrame(
        {
            "days_to_expiry": days,
            "tenure_months": tenure,
            "prior_renewals": prior,
            "late_payment_ratio": late,
            "nsf_count_12m": nsf,
            "open_work_orders": open_wo,
            "avg_maintenance_days": maint,
            "unresolved_work_orders": unresolved,
            "portal_logins_30d": logins,
            "csat": csat,
            "auto_pay": auto,
            "neighborhood_vacancy": vacancy,
            "building_recent_moveouts": moveouts,
            "rent_to_market": rent_to_market,
            "rent_increase_offered_pct": increase,
            "monthly_rent": rent,
            "churned": y,
        }
    )
    return frame


def train_churn_model(output: Path | None = None, n: int = 800) -> Path:
    settings = get_settings()
    output = output or settings.churn_model_path
    output.parent.mkdir(parents=True, exist_ok=True)
    frame = _synthetic_training_frame(n=n)
    train = lgb.Dataset(frame[FEATURE_COLUMNS], label=frame["churned"])
    booster = lgb.train(
        {
            "objective": "binary",
            "metric": "auc",
            "learning_rate": 0.05,
            "num_leaves": 24,
            "min_data_in_leaf": 20,
            "feature_fraction": 0.85,
            "verbosity": -1,
            "seed": 7,
        },
        train,
        num_boost_round=120,
    )
    booster.save_model(str(output))
    return output


def load_or_train() -> lgb.Booster:
    settings = get_settings()
    path = settings.churn_model_path
    if not path.exists():
        train_churn_model(path)
    return lgb.Booster(model_file=str(path))
