from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from acreops.config import get_settings

settings = get_settings()
settings.acreops_data_dir = ROOT / "data"
settings.acreops_artifact_dir = ROOT / "artifacts"
settings.churn_model_path = ROOT / "artifacts" / "churn_lightgbm.txt"
