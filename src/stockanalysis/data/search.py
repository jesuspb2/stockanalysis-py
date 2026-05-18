from __future__ import annotations

from typing import Any

import pandas as pd

from stockanalysis.core.http import BASE, resolve
from stockanalysis.core.session import get_session

_SCREENER_COLUMNS = "s,n,marketCap,price,change,revenue,netIncome,peRatio,sector"


def search(query: str) -> list[dict[str, Any]]:
    """
    Search for stocks, ETFs, and indices by name or symbol.

    Returns a list of dicts with keys: symbol, name, type.

    Usage:
        import stockanalysis as sa
        sa.search("Apple")   # [{"symbol": "AAPL", "name": "Apple Inc.", "type": "stock"}, …]
    """
    url = f"{BASE}/search/__data.json"
    resp = get_session().get(
        url,
        params={"q": query},
        headers={"Referer": f"{BASE}/search/"},
        timeout=15,
    )
    resp.raise_for_status()
    payload = resp.json()
    node_data = payload["nodes"][2]["data"]
    meta = node_data[0]
    raw = resolve(meta.get("results", meta.get("searchResults", 0)), node_data)
    if not isinstance(raw, list):
        return []
    results = []
    for item in raw:
        if isinstance(item, dict):
            results.append(
                {
                    "symbol": item.get("s") or item.get("symbol"),
                    "name": item.get("n") or item.get("name"),
                    "type": item.get("type", "stock"),
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
        price, change, revenue, netIncome, peRatio, sector.

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

    url = f"{BASE}/screener/stock/__data.json"
    resp = get_session().get(
        url,
        params=params,
        headers={"Referer": f"{BASE}/screener/stock/"},
        timeout=30,
    )
    resp.raise_for_status()
    payload = resp.json()
    node_data = payload["nodes"][2]["data"]
    meta = node_data[0]
    raw = resolve(meta.get("data", 0), node_data)
    if not isinstance(raw, list):
        return pd.DataFrame()
    df = pd.DataFrame(raw)
    rename = {"s": "symbol", "n": "name"}
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    return df
