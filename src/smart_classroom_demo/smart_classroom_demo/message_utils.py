"""Helpers for compact String message payloads used in the demo."""

from __future__ import annotations

from collections.abc import Iterable


def build_payload(**fields: object) -> str:
    """Encode key-value fields into a readable String payload."""
    parts = []
    for key, value in fields.items():
        text = stringify_value(value).replace("|", "/").strip()
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


def parse_csv_field(value: str) -> list[str]:
    """Parse a comma-separated field produced by stringify_value()."""
    if not value or value == "-":
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def stringify_value(value: object) -> str:
    """Convert supported values into compact payload text."""
    if isinstance(value, str):
        return value
    if isinstance(value, Iterable) and not isinstance(
        value, (bytes, bytearray, dict)
    ):
        return ",".join(str(item) for item in value)
    return str(value)
