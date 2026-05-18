from __future__ import annotations

from typing import Any, cast

import pandas as pd

from stockanalysis.core.session import get_session

BASE = "https://stockanalysis.com"

_cache: dict[tuple[str, tuple[tuple[str, str], ...]], list[Any]] = {}


def fetch_data_json(
    path: str, params: dict[str, str] | None = None, timeout: int = 15
) -> list[Any]:
    """Fetch a SvelteKit __data.json endpoint and return the node_data array."""
    key = (path, tuple(sorted((params or {}).items())))
    if key in _cache:
        return _cache[key]
    url = f"{BASE}{path}/__data.json"
    headers = {"Referer": f"{BASE}{path}/"}
    resp = get_session().get(url, params=params or {}, headers=headers, timeout=timeout)
    resp.raise_for_status()
    data = cast(list[Any], resp.json()["nodes"][2]["data"])
    _cache[key] = data
    return data


def clear_cache() -> None:
    """Clear the in-memory HTTP response cache."""
    _cache.clear()


def resolve(val: Any, d: list[Any]) -> Any:
    """Recursively resolve SvelteKit deduplicated index references."""
    if isinstance(val, int) and 0 <= val < len(d):
        v = d[val]
        if isinstance(v, dict):
            return {k: resolve(vv, d) for k, vv in v.items()}
        if isinstance(v, list):
            return [resolve(x, d) for x in v]
        return v
    return val


def resolve_meta(node_data: list[Any]) -> dict[str, Any]:
    """Resolve every key in the top-level meta dict."""
    meta = node_data[0]
    return {k: resolve(v, node_data) for k, v in meta.items()}


def extract_financial_df(
    node_data: list[Any], key: str = "financialData"
) -> pd.DataFrame:
    """Extract a financial DataFrame from node_data using SvelteKit dedup encoding."""
    meta = node_data[0]
    fd_refs = node_data[meta[key]]
    resolved = {k: resolve(v, node_data) for k, v in fd_refs.items()}
    dates = resolved.pop("datekey", [])
    df = pd.DataFrame(resolved, index=dates)
    df.index.name = "period"
    return df


def extract_metrics_df(node_data: list[Any]) -> pd.DataFrame:
    """Extract financials/metrics page into a flat DataFrame (all categories merged)."""
    meta = node_data[0]
    fd = resolve(meta["financialData"], node_data)
    dates = fd["datekey"]
    columns: dict[str, list[Any]] = {}
    for metrics in fd["categories"].values():
        for metric_id, values in metrics.items():
            columns[metric_id] = values
    df = pd.DataFrame(columns, index=dates)
    df.index.name = "period"
    return df
