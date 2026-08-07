"""Aggregate adapter health for degraded-mode decisions."""

from __future__ import annotations

from typing import Any

from meeting_core.adapters.base import Adapter, HealthStatus


def aggregate_health(adapters: dict[str, Adapter]) -> dict[str, Any]:
    details: dict[str, Any] = {}
    unhealthy: list[str] = []
    degraded: list[str] = []
    for name, adapter in adapters.items():
        status: HealthStatus = adapter.health()
        details[name] = {
            "healthy": status.healthy,
            "degraded": status.degraded,
            "latency_ms": status.latency_ms,
            "detail": status.detail,
            "capabilities": adapter.capabilities().__dict__,
        }
        if not status.healthy:
            unhealthy.append(name)
        elif status.degraded:
            degraded.append(name)
    overall = "ok"
    if unhealthy:
        overall = "degraded" if len(unhealthy) < len(adapters) else "down"
    elif degraded:
        overall = "degraded"
    return {
        "overall": overall,
        "unhealthy": unhealthy,
        "degraded": degraded,
        "adapters": details,
    }
