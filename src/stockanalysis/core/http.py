from __future__ import annotations

from typing import Any, cast

import pandas as pd

from stockanalysis.core.session import get_session

BASE = "https://stockanalysis.com"

_cache: dict[tuple[str, tuple[tuple[str, str], ...], tuple[str, ...]], list[Any]] = {}


def fetch_data_json(
    path: str,
    params: dict[str, str] | None = None,
    timeout: int = 15,
    prefer_keys: tuple[str, ...] | None = None,
) -> list[Any]:
    """Fetch a SvelteKit __data.json endpoint and return the node_data array.

    prefer_keys: if given, pick the first data node whose data[0] contains any
    of these keys instead of defaulting to the last data node.  Used when the
    page-specific node appears before the layout node in the nodes array.
    """
    cache_key = (path, tuple(sorted((params or {}).items())), prefer_keys or ())
    if cache_key in _cache:
        return _cache[cache_key]
    url = f"{BASE}{path}/__data.json"
    headers = {"Referer": f"{BASE}{path}/"}
    resp = get_session().get(url, params=params or {}, headers=headers, timeout=timeout)
    resp.raise_for_status()
    nodes = resp.json()["nodes"]

    data_node = None
    if prefer_keys:
        for n in nodes:
            if (
                isinstance(n, dict)
                and n.get("type") == "data"
                and "data" in n
                and isinstance(n["data"], list)
                and n["data"]
                and isinstance(n["data"][0], dict)
                and any(k in n["data"][0] for k in prefer_keys)
            ):
                data_node = n
                break

    if data_node is None:
        data_node = next(
            (
                n
                for n in reversed(nodes)
                if isinstance(n, dict) and n.get("type") == "data" and "data" in n
            ),
            None,
        )

    if data_node is None:
        error_node = next(
            (n for n in nodes if isinstance(n, dict) and n.get("type") == "error"), None
        )
        msg = (
            error_node["error"].get("message", "unknown")
            if error_node
            else "no data node found"
        )
        raise ValueError(f"API returned no data: {msg}")
    data = cast(list[Any], data_node["data"])
    _cache[cache_key] = data
    return data


def clear_cache() -> None:
    """Clear the in-memory HTTP response cache."""
    _cache.clear()


_SUFFIXES = {"T": 1e12, "B": 1e9, "M": 1e6, "K": 1e3}


def parse_numeric(s: Any) -> Any:
    """Parse a human-formatted number string to float.

    Handles: '$766.97B' → 766970000000.0, '4.37T' → 4.37e12, '0.09%' → 0.09.
    Returns s unchanged if it cannot be cleanly parsed as a single number.
    """
    if not isinstance(s, str):
        return s
    v = s.strip().replace(",", "")
    if v.startswith("$"):
        v = v[1:]
    if " " in v or "(" in v:
        return s
    if v.endswith("%"):
        try:
            return float(v[:-1])
        except ValueError:
            return s
    for suffix, mult in _SUFFIXES.items():
        if v.endswith(suffix):
            try:
                return float(v[:-1]) * mult
            except ValueError:
                return s
    try:
        return float(v)
    except ValueError:
        return s


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
