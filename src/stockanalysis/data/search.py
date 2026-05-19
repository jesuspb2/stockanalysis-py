from __future__ import annotations

from typing import Any

import pandas as pd

from stockanalysis.core.http import BASE, fetch_data_json, resolve
from stockanalysis.core.session import get_session

_SCREENER_COLUMNS = "s,n,marketCap,price,change,industry,peRatio"

_VALID_SECTORS = (
    "Communication Services",
    "Consumer Discretionary",
    "Consumer Staples",
    "Energy",
    "Financials",
    "Healthcare",
    "Industrials",
    "Materials",
    "Real Estate",
    "Technology",
    "Utilities",
)

_TYPE_MAP = {"s": "stock", "e": "etf", "i": "index", "sy": "stock"}


def search(query: str) -> list[dict[str, Any]]:
    """
    Search for stocks, ETFs, and indices by name or symbol.

    Returns a list of dicts with keys: symbol, name, type.

    Usage:
        import stockanalysis as sa
        sa.search("Apple")   # [{"symbol": "AAPL", "name": "Apple Inc.", "type": "stock"}, …]
    """
    try:
        resp = get_session().get(
            f"{BASE}/api/search",
            params={"q": query},
            headers={"Referer": f"{BASE}/"},
            timeout=15,
        )
        resp.raise_for_status()
        payload = resp.json()
    except Exception:
        return []
    raw = payload.get("data", [])
    if not isinstance(raw, list):
        return []
    results = []
    for item in raw:
        if isinstance(item, dict):
            results.append(
                {
                    "symbol": item.get("s") or item.get("symbol"),
                    "name": item.get("n") or item.get("name"),
                    "type": _TYPE_MAP.get(item.get("t", ""), "stock"),
                }
            )
    return results


def _fetch_sector_symbols(sector: str) -> set[str]:
    if sector not in _VALID_SECTORS:
        raise ValueError(
            f"Invalid sector {sector!r}. Must be one of: {list(_VALID_SECTORS)}"
        )
    slug = sector.lower().replace(" ", "-")
    node_data = fetch_data_json(
        f"/stocks/sector/{slug}", params={"count": "10000"}, timeout=30
    )
    meta = node_data[0]
    raw = resolve(meta.get("data", 0), node_data)
    if not isinstance(raw, list):
        return set()
    return {item["s"] for item in raw if isinstance(item, dict) and "s" in item}


def screener(
    market_cap_min: float | None = None,
    market_cap_max: float | None = None,
    sector: str | None = None,
    country: str | None = None,
    exchange: str | None = None,
    **extra_params: str,
) -> pd.DataFrame:
    """
    Screen stocks using stockanalysis.com's screener.

    Args:
        market_cap_min: Minimum market cap in USD (e.g. 10e9 for $10B).
        market_cap_max: Maximum market cap in USD.
        sector: Sector name. Must be one of the 11 valid sectors:
            "Communication Services", "Consumer Discretionary", "Consumer Staples",
            "Energy", "Financials", "Healthcare", "Industrials", "Materials",
            "Real Estate", "Technology", "Utilities".
        country: Country code (e.g. "US", "CN").
        exchange: Exchange (e.g. "NYSE", "NASDAQ").
        **extra_params: Any additional raw filter params passed to the endpoint.

    Returns:
        DataFrame with one row per stock and columns: symbol, name, marketCap,
        price, change, industry, volume, peRatio.

    Usage:
        import stockanalysis as sa
        sa.screener(sector="Technology", market_cap_min=10e9)
    """
    params: dict[str, str] = {"columns": _SCREENER_COLUMNS}
    params.update(extra_params)

    node_data = fetch_data_json("/stocks/screener", params=params, timeout=30)
    meta = node_data[0]
    raw = resolve(meta.get("data", 0), node_data)
    if not isinstance(raw, list):
        return pd.DataFrame()
    df = pd.DataFrame(raw)
    rename = {"s": "symbol", "n": "name"}
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    if sector is not None:
        sector_syms = _fetch_sector_symbols(sector)
        df = df[df["symbol"].isin(sector_syms)].reset_index(drop=True)
    if market_cap_min is not None and "marketCap" in df.columns:
        df = df[df["marketCap"] >= market_cap_min].reset_index(drop=True)
    if market_cap_max is not None and "marketCap" in df.columns:
        df = df[df["marketCap"] <= market_cap_max].reset_index(drop=True)

    return df
