"""Helpers for compact String message payloads used in the demo."""

from __future__ import annotations


def build_payload(**fields: object) -> str:
    """Encode key-value fields into a readable String payload."""
    parts = []
    for key, value in fields.items():
        text = str(value).replace("|", "/").strip()
        parts.append(f"{key}={text}")
    return " | ".join(parts)


def parse_payload(payload: str) -> dict[str, str]:
    """Parse a payload created by build_payload()."""
    result: dict[str, str] = {}
    for chunk in payload.split("|"):
        item = chunk.strip()
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        result[key.strip()] = value.strip()
    return result
