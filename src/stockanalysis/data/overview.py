from __future__ import annotations

from typing import Any

from stockanalysis.core.http import fetch_data_json, resolve

_SCALAR_KEYS = [
    "marketCap",
    "revenue",
    "netIncome",
    "eps",
    "peRatio",
    "forwardPE",
    "dividend",
    "exDividendDate",
    "beta",
    "analysts",
    "target",
    "earningsDate",
    "description",
]


def fetch_overview(symbol: str) -> dict[str, Any]:
    """Summary data from the main stock page."""
    node_data = fetch_data_json(f"/stocks/{symbol.lower()}")
    meta = node_data[0]
    result: dict[str, Any] = {}
    for key in _SCALAR_KEYS:
        if key in meta:
            result[key] = resolve(meta[key], node_data)
    info_rows = resolve(meta.get("infoTable", 0), node_data)
    if isinstance(info_rows, list):
        result["infoTable"] = {
            row["t"]: row["v"] for row in info_rows if "t" in row and "v" in row
        }
    return result
