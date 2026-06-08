from __future__ import annotations

import datetime
from typing import Any, Literal, cast

import pandas as pd

from stockanalysis.core.http import fetch_data_json, resolve

Period = Literal["annual", "quarterly"]


class Forecasts:
    """Analyst estimates and price targets for a stock."""

    def __init__(self, symbol: str) -> None:
        self._symbol = symbol.lower()

    def _fetch(self) -> tuple[list[Any], dict[str, Any]]:
        node_data = fetch_data_json(f"/stocks/{self._symbol}/forecast")
        return node_data, node_data[0]

    def estimates(self, period: Period = "annual") -> pd.DataFrame:
        """
        Analyst consensus estimates (revenue, EPS, EBITDA, net income…).

        Returns a DataFrame indexed by fiscal period date.
        Pro values show up as actual numbers when authenticated.
        """
        node_data, meta = self._fetch()
        table = resolve(meta["estimates"], node_data)
        data = table["table"][period]

        dates = data.pop("dates", [])
        df = pd.DataFrame(data, index=dates)
        df.index.name = "period"
        if "analysts" in df.columns:
            df = df.rename(columns={"analysts": "no_analysts"})
            df["no_analysts"] = pd.to_numeric(
                df["no_analysts"], errors="coerce"
            ).astype("Int64")
        today = datetime.date.today().isoformat()
        df["is_estimate"] = [str(d) >= today for d in df.index]
        return df

    def revenue(self, period: Period = "annual") -> pd.Series:
        """Analyst revenue estimates as a Series indexed by fiscal period."""
        return self.estimates(period=period)["revenue"]

    def eps(self, period: Period = "annual") -> pd.Series:
        """Analyst EPS estimates as a Series indexed by fiscal period."""
        return self.estimates(period=period)["eps"]

    def price_targets(self) -> dict[str, Any]:
        """
        Analyst price targets summary: high, low, average, median, current, num_price_targets.

        Returns a plain dict.
        """
        node_data, meta = self._fetch()
        raw = cast(dict[str, Any], resolve(meta["priceTargets"], node_data))

        # Derive current price from the targets chart (monthly, last non-null close)
        targets_node = resolve(meta.get("targets", {}), node_data)
        chart = targets_node.get("chart", []) if isinstance(targets_node, dict) else []
        current = next(
            (
                row["c"]
                for row in reversed(chart)
                if isinstance(row, dict) and row.get("c") is not None
            ),
            None,
        )

        return {
            "high": raw.get("high"),
            "low": raw.get("low"),
            "average": raw.get("avg"),
            "median": raw.get("median"),
            "current": current,
            "num_price_targets": raw.get("numPriceTargets"),
        }

    def recommendations(self) -> pd.DataFrame:
        """
        Analyst buy/hold/sell recommendation breakdown over time.

        Returns a DataFrame indexed by date with columns: strongBuy, buy, hold, sell, strongSell.
        """
        node_data, meta = self._fetch()
        rows = resolve(meta["recommendations"], node_data)
        if not isinstance(rows, list):
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        df = df.drop(
            columns=[c for c in ("filtered", "month", "updated") if c in df.columns]
        )
        if "date" in df.columns:
            df = df.set_index("date")
            df.index.name = "date"
        return df
