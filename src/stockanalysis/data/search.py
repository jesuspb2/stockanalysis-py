from __future__ import annotations

from typing import Any

import pandas as pd

from stockanalysis.core.http import BASE, fetch_data_json, resolve
from stockanalysis.core.session import get_session

_SCREENER_API = "/_api/endpoints/screener/data-point"

# Filters that are already present in the default screener response columns
_DIRECT_FILTER_MAP: dict[str, str] = {
    "price": "price",
    "pe_ratio": "peRatio",
    "volume": "volume",
    "change": "change",
}

# Filters that require a separate data-point API call: snake_case key → data-point ID
_FILTER_ID_MAP: dict[str, str] = {
    "dividend_yield": "dividendYield",
    "pe_forward": "peForward",
    "pb_ratio": "pbRatio",
    "ps_ratio": "psRatio",
    "ev_ebitda": "evEbitda",
    "peg_ratio": "pegRatio",
    "revenue_growth": "revenueGrowth",
    "eps_growth": "epsGrowth",
    "gross_margin": "grossMargin",
    "operating_margin": "operatingMargin",
    "net_margin": "profitMargin",
    "roe": "roe",
    "roic": "roic",
    "debt_equity": "debtEquity",
    "current_ratio": "currentRatio",
    "price_change_1y": "ch1y",
    "rsi": "rsi",
    "beta": "beta",
    "avg_volume": "averageVolume",
}

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


def _fetch_datapoint_symbols(data_id: str, value: str) -> set[str]:
    resp = get_session().get(
        f"{BASE}{_SCREENER_API}",
        params={"type": "s", "id": data_id},
        headers={"Referer": f"{BASE}/stocks/screener/"},
        timeout=30,
    )
    resp.raise_for_status()
    pairs = resp.json().get("data", {}).get("data", [])
    return {sym for sym, val in pairs if isinstance(val, str) and val.lower() == value.lower()}


def _fetch_datapoint_numeric(data_id: str) -> dict[str, float]:
    resp = get_session().get(
        f"{BASE}{_SCREENER_API}",
        params={"type": "s", "id": data_id},
        headers={"Referer": f"{BASE}/stocks/screener/"},
        timeout=30,
    )
    resp.raise_for_status()
    pairs = resp.json().get("data", {}).get("data", [])
    result: dict[str, float] = {}
    for sym, val in pairs:
        try:
            result[sym] = float(val)
        except (TypeError, ValueError):
            pass
    return result


def screener(
    market_cap_min: float | None = None,
    market_cap_max: float | None = None,
    sector: str | None = None,
    country: str | None = None,
    exchange: str | None = None,
    filters: dict[str, tuple[float | None, float | None]] | None = None,
    **extra_params: str,
) -> pd.DataFrame:
    """
    Screen stocks using stockanalysis.com's screener.

    Args:
        market_cap_min: Minimum market cap in USD (e.g. 10e9 for $10B).
        market_cap_max: Maximum market cap in USD.
        sector: One of the 11 GICS sectors (e.g. "Technology", "Healthcare").
        country: Country name as shown on stockanalysis.com (e.g. "United States", "China").
        exchange: Exchange name (e.g. "NYSE", "NASDAQ", "NYSEAMERICAN").
        filters: Dict of numeric range filters as {key: (min, max)}, where None means
            unbounded. Available keys:

            Price & Volume:
                price, volume, change, avg_volume, beta, rsi

            Valuation:
                pe_ratio, pe_forward, pb_ratio, ps_ratio, peg_ratio,
                ev_ebitda, dividend_yield

            Growth:
                revenue_growth, eps_growth, price_change_1y

            Profitability:
                gross_margin, operating_margin, net_margin, roe, roic

            Financial Strength:
                debt_equity, current_ratio

        **extra_params: Raw query params forwarded to the screener endpoint.

    Returns:
        DataFrame with columns: symbol, name, marketCap, price, change,
        industry, volume, peRatio.

    Usage:
        import stockanalysis as sa

        # Tech large-caps with decent yield and low PE
        sa.screener(
            sector="Technology",
            market_cap_min=10e9,
            filters={
                "dividend_yield": (1, None),
                "pe_ratio": (None, 30),
                "revenue_growth": (5, None),
            },
        )
    """
    if filters:
        unknown = set(filters) - set(_DIRECT_FILTER_MAP) - set(_FILTER_ID_MAP)
        if unknown:
            valid = sorted(set(_DIRECT_FILTER_MAP) | set(_FILTER_ID_MAP))
            raise ValueError(f"Unknown filter(s): {sorted(unknown)}. Valid: {valid}")

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
    if country is not None:
        country_syms = _fetch_datapoint_symbols("country", country)
        df = df[df["symbol"].isin(country_syms)].reset_index(drop=True)
    if exchange is not None:
        exchange_syms = _fetch_datapoint_symbols("exchange", exchange)
        df = df[df["symbol"].isin(exchange_syms)].reset_index(drop=True)
    if market_cap_min is not None and "marketCap" in df.columns:
        df = df[df["marketCap"] >= market_cap_min].reset_index(drop=True)
    if market_cap_max is not None and "marketCap" in df.columns:
        df = df[df["marketCap"] <= market_cap_max].reset_index(drop=True)

    if filters:
        for key, bounds in filters.items():
            low, high = bounds
            if key in _DIRECT_FILTER_MAP:
                col = _DIRECT_FILTER_MAP[key]
                if col in df.columns:
                    if low is not None:
                        df = df[df[col] >= low].reset_index(drop=True)
                    if high is not None:
                        df = df[df[col] <= high].reset_index(drop=True)
            else:
                values = _fetch_datapoint_numeric(_FILTER_ID_MAP[key])
                syms = {
                    s for s, v in values.items()
                    if (low is None or v >= low) and (high is None or v <= high)
                }
                df = df[df["symbol"].isin(syms)].reset_index(drop=True)

    return df
