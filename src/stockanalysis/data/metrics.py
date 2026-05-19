from __future__ import annotations

from typing import Any, Literal

import pandas as pd

from stockanalysis.core.http import fetch_data_json, resolve

Period = Literal["quarterly", "trailing", "annual"]

# "annual" is accepted as an alias for "trailing" so callers that learn
# period="annual" from financials.* don't silently get empty results here.
_PERIOD_ALIAS: dict[str, str] = {"annual": "trailing"}


def _segment_df(node_data: list[Any], period: Period = "quarterly") -> pd.DataFrame:
    """Parse a segment-breakdown metrics endpoint into a pivoted DataFrame."""
    resolved_period = _PERIOD_ALIAS.get(period, period)
    meta = node_data[0]
    data_ref = meta.get("data")
    if data_ref is None:
        return pd.DataFrame()
    data_top = resolve(data_ref, node_data)
    segments: list[dict[str, Any]] = data_top.get("data", {}).get(resolved_period, [])
    if not segments:
        return pd.DataFrame()
    return _series_list_to_df(segments)


def _series_list_to_df(segments: list[dict[str, Any]]) -> pd.DataFrame:
    rows: dict[str, dict[str, float | None]] = {}
    for seg in segments:
        name = seg["name"]
        for point in seg["values"]:
            date = point["x"]
            rows.setdefault(date, {})[name] = point["y"]
    df = pd.DataFrame.from_dict(rows, orient="index")
    df.index = pd.to_datetime(df.index)
    df.index.name = "date"
    df.sort_index(inplace=True)
    return df


class Metrics:
    """Segment and breakdown metrics for a stock."""

    def __init__(self, symbol: str) -> None:
        self._symbol = symbol.lower()

    def _fetch(self, path_suffix: str, period: Period) -> pd.DataFrame:
        node_data = fetch_data_json(f"/stocks/{self._symbol}/{path_suffix}")
        return _segment_df(node_data, period)

    def revenue_by_segment(self, period: Period = "quarterly") -> pd.DataFrame:
        """Revenue broken down by product/service segment."""
        return self._fetch("metrics/revenue-by-segment", period)

    def gross_profit_by_type(self, period: Period = "quarterly") -> pd.DataFrame:
        """Gross profit broken down by segment type."""
        return self._fetch("metrics/gross-profit-by-type", period)

    def gross_margin_by_type(self, period: Period = "quarterly") -> pd.DataFrame:
        """Gross margin (%) broken down by segment type."""
        return self._fetch("metrics/gross-margin-by-type", period)

    def revenue_by_geography(self, period: Period = "quarterly") -> pd.DataFrame:
        """Revenue broken down by geography."""
        return self._fetch("metrics/revenue-by-geography", period)

    def operating_expense_breakdown(self, period: Period = "quarterly") -> pd.DataFrame:
        """Operating expenses broken down by category."""
        return self._fetch("metrics/operating-expense-breakdown", period)

    def operating_metrics(self) -> pd.DataFrame:
        """Annual operating metrics unique to the /metrics/ overview page (e.g. active devices)."""
        node_data = fetch_data_json(f"/stocks/{self._symbol}/metrics")
        data = resolve(node_data[0]["data"], node_data)
        return _series_list_to_df(data["annualMetrics"])
