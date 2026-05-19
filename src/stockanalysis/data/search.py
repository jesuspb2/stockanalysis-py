from __future__ import annotations

from typing import Any

import pandas as pd

from stockanalysis.core.http import BASE, fetch_data_json, resolve
from stockanalysis.core.session import get_session

_SCREENER_COLUMNS = "s,n,marketCap,price,change,sector,peRatio"


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
        sector: Sector name (e.g. "Technology", "Healthcare").
        country: Country code (e.g. "US", "CN").
        exchange: Exchange (e.g. "NYSE", "NASDAQ").
        **extra_params: Any additional raw filter params passed to the endpoint.

    Returns:
        DataFrame with one row per stock and columns: symbol, name, marketCap,
        price, change, sector, volume, peRatio.

    Usage:
        import stockanalysis as sa
        sa.screener(sector="Technology", market_cap_min=10e9)
    """
    params: dict[str, str] = {"columns": _SCREENER_COLUMNS}
    if market_cap_min is not None:
        params["f[marketCap][gte]"] = str(int(market_cap_min))
    if market_cap_max is not None:
        params["f[marketCap][lte]"] = str(int(market_cap_max))
    if sector is not None:
        params["f[sector]"] = sector
    if country is not None:
        params["f[country]"] = country
    if exchange is not None:
        params["f[exchange]"] = exchange
    params.update(extra_params)

    node_data = fetch_data_json("/stocks/screener", params=params, timeout=30)
    meta = node_data[0]
    raw = resolve(meta.get("data", 0), node_data)
    if not isinstance(raw, list):
        return pd.DataFrame()
    df = pd.DataFrame(raw)
    rename = {"s": "symbol", "n": "name"}
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    if sector is not None and "sector" in df.columns:
        df = df[df["sector"] == sector].reset_index(drop=True)
    return df
