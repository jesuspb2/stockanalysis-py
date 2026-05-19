from __future__ import annotations

from typing import Any

from stockanalysis.core.http import fetch_data_json, parse_numeric, resolve

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

_NUMERIC_KEYS = {
    "marketCap",
    "revenue",
    "netIncome",
    "eps",
    "peRatio",
    "forwardPE",
    "beta",
}


def fetch_overview(symbol: str) -> dict[str, Any]:
    """Summary data from the main stock page."""
    node_data = fetch_data_json(f"/stocks/{symbol.lower()}")
    meta = node_data[0]
    result: dict[str, Any] = {}
    for key in _SCALAR_KEYS:
        if key in meta:
            val = resolve(meta[key], node_data)
            if key in _NUMERIC_KEYS:
                val = parse_numeric(val)
                if key == "marketCap" and isinstance(val, float) and val.is_integer():
                    val = int(val)
            result[key] = val
    return result
