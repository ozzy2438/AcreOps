from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from acreops.config import get_settings


def _data_dir() -> Path:
    settings = get_settings()
    candidate = settings.acreops_data_dir
    if candidate.exists():
        return candidate
    return Path(__file__).resolve().parents[3] / "data"


@lru_cache(maxsize=16)
def load_json(name: str) -> Any:
    path = _data_dir() / name
    if not path.exists():
        raise FileNotFoundError(f"Demo catalog missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def parcels() -> list[dict[str, Any]]:
    return load_json("parcels.json")


def vendors() -> list[dict[str, Any]]:
    return load_json("vendors.json")


def permits() -> list[dict[str, Any]]:
    return load_json("permits.json")


def tenants() -> list[dict[str, Any]]:
    return load_json("tenants.json")


def bim_models() -> list[dict[str, Any]]:
    return load_json("bim_models.json")


def find_parcel(address: str | None = None, parcel_id: str | None = None) -> dict[str, Any] | None:
    needle_addr = (address or "").lower().strip()
    for parcel in parcels():
        if parcel_id and parcel.get("parcel_id") == parcel_id:
            return parcel
        if needle_addr and needle_addr in parcel.get("address", "").lower():
            return parcel
        if needle_addr and needle_addr in f"{parcel.get('address', '')} {parcel.get('city', '')}".lower():
            return parcel
    return parcels()[0] if parcels() else None
