from __future__ import annotations

from typing import Literal

import pandas as pd

from stockanalysis.core.http import fetch_data_json, resolve

Period = Literal["annual", "quarterly"]


class Forecasts:
    """Analyst estimates and price targets for a stock."""

    def __init__(self, symbol: str) -> None:
        self._symbol = symbol.lower()

    def _fetch(self) -> tuple[list, dict]:
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
        return df

    def revenue(self, period: Period = "annual") -> pd.Series:
        """Analyst revenue estimates as a Series indexed by fiscal period."""
        return self.estimates(period=period)["revenue"]

    def eps(self, period: Period = "annual") -> pd.Series:
        """Analyst EPS estimates as a Series indexed by fiscal period."""
        return self.estimates(period=period)["eps"]

    def price_targets(self) -> dict:
        """
        Analyst price targets summary (high, low, average, current).

        Returns a plain dict.
        """
        node_data, meta = self._fetch()
        return resolve(meta["priceTargets"], node_data)

    def recommendations(self) -> pd.DataFrame:
        """
        Analyst buy/hold/sell recommendation breakdown over time.

        Returns a DataFrame with columns: strongBuy, buy, hold, sell, strongSell.
        """
        node_data, meta = self._fetch()
        rows = resolve(meta["recommendations"], node_data)
        if not isinstance(rows, list):
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        if "date" in df.columns:
            df = df.set_index("date")
            df.index.name = "date"
        return df
