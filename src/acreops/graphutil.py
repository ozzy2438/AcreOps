from __future__ import annotations

from typing import Annotated, Any


def append_list(left: list[Any] | None, right: list[Any] | None) -> list[Any]:
    return list(left or []) + list(right or [])


AuditTrail = Annotated[list[dict[str, Any]], append_list]
