from __future__ import annotations

from typing import Any

import pandas as pd

from stockanalysis.core.http import fetch_data_json, resolve

_OVERVIEW_KEYS = [
    "description",
    "expenseRatio",
    "aum",
    "nav",
    "inceptionDate",
    "index",
    "category",
    "issuer",
    "assetClass",
    "numHoldings",
    "dividend",
    "dividendYield",
    "pe",
    "beta",
]


def fetch_etf_overview(symbol: str) -> dict[str, Any]:
    """Summary data from the main ETF page (AUM, expense ratio, description…)."""
    node_data = fetch_data_json(f"/etf/{symbol.lower()}")
    meta = node_data[0]
    result: dict[str, Any] = {}
    for key in _OVERVIEW_KEYS:
        if key in meta:
            result[key] = resolve(meta[key], node_data)
    info_rows = resolve(meta.get("infoTable", 0), node_data)
    if isinstance(info_rows, list):
        result["infoTable"] = {
            row["t"]: row["v"] for row in info_rows if "t" in row and "v" in row
        }
    return result


def fetch_etf_sectors(symbol: str) -> pd.DataFrame:
    """Sector allocation as a DataFrame with columns: sector, weight."""
    node_data = fetch_data_json(f"/etf/{symbol.lower()}")
    meta = node_data[0]
    raw = resolve(meta.get("sectorBreakdown", meta.get("sectors", 0)), node_data)
    if isinstance(raw, dict):
        df = pd.DataFrame(list(raw.items()), columns=["sector", "weight"])
    elif isinstance(raw, list):
        df = pd.DataFrame(raw)
    else:
        return pd.DataFrame(columns=["sector", "weight"])
    return df


def fetch_etf_performance(symbol: str) -> pd.DataFrame:
    """Returns by period (1m, 3m, 6m, YTD, 1y, 3y, 5y, 10y)."""
    node_data = fetch_data_json(f"/etf/{symbol.lower()}/performance")
    meta = node_data[0]
    raw = resolve(meta.get("performance", meta.get("data", 0)), node_data)
    if isinstance(raw, list):
        return pd.DataFrame(raw)
    if isinstance(raw, dict):
        return pd.DataFrame(list(raw.items()), columns=["period", "return"])
    return pd.DataFrame(columns=["period", "return"])
