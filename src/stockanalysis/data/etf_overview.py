from __future__ import annotations

from typing import Any

import pandas as pd

from stockanalysis.core.http import fetch_data_json, parse_numeric, resolve

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

_ETF_NUMERIC_KEYS = {"expenseRatio", "aum", "nav", "dividendYield", "pe", "beta"}


def fetch_etf_overview(symbol: str) -> dict[str, Any]:
    """Summary data from the main ETF page (AUM, expense ratio, description…)."""
    node_data = fetch_data_json(f"/etf/{symbol.lower()}")
    meta = node_data[0]
    result: dict[str, Any] = {}
    for key in _OVERVIEW_KEYS:
        if key in meta:
            val = resolve(meta[key], node_data)
            result[key] = parse_numeric(val) if key in _ETF_NUMERIC_KEYS else val
    info_rows = resolve(meta.get("infoTable", 0), node_data)
    if isinstance(info_rows, list):
        result["infoTable"] = {
            row["t"]: row["v"] for row in info_rows if "t" in row and "v" in row
        }
    return result


def fetch_etf_sectors(symbol: str) -> pd.DataFrame:
    """Sector allocation as a DataFrame with columns: sector, weight."""
    node_data = fetch_data_json(
        f"/etf/{symbol.lower()}/holdings",
        prefer_keys=("sectors", "holdings", "asset_allocation"),
    )
    meta = node_data[0]
    raw = resolve(meta.get("sectors", []), node_data)
    if not isinstance(raw, list) or not raw:
        return pd.DataFrame(columns=["sector", "weight"])
    df = pd.DataFrame(raw)
    df = df.rename(columns={"n": "sector", "w": "weight"})
    return df[["sector", "weight"]]


_PERF_RENAME = {
    "tr1m": "1m",
    "trYTD": "YTD",
    "tr1y": "1y",
    "cagr3y": "3y_cagr",
    "cagr5y": "5y_cagr",
    "cagr10y": "10y_cagr",
    "cagrMAX": "max_cagr",
}


def fetch_etf_performance(symbol: str) -> pd.DataFrame:
    """Returns by period (1m, YTD, 1y, 5y_cagr, 10y_cagr, max_cagr)."""
    node_data = fetch_data_json(f"/etf/{symbol.lower()}")
    meta = node_data[0]
    raw = resolve(meta.get("performance", 0), node_data)
    if not isinstance(raw, dict):
        return pd.DataFrame(columns=["period", "return"])
    renamed = {_PERF_RENAME.get(k, k): v for k, v in raw.items()}
    return pd.DataFrame(list(renamed.items()), columns=["period", "return"])
