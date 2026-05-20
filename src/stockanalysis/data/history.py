from __future__ import annotations

from typing import Literal

import pandas as pd

from stockanalysis.core.http import fetch_data_json, resolve
from stockanalysis.core.session import get_session

_API_BASE = "https://stockanalysis.com/api/symbol/s"

Frequency = Literal["daily", "weekly", "monthly", "quarterly", "annual"]


class History:
    """Historical price data and market cap history."""

    def __init__(self, symbol: str) -> None:
        self._symbol = symbol.lower()

    def prices(self) -> pd.DataFrame:
        """
        Full daily close price history (from IPO).

        Returns a DataFrame indexed by date with a single column: close.
        """
        url = f"{_API_BASE}/{self._symbol}/history"
        resp = get_session().get(url, params={"type": "chart"}, timeout=15)
        resp.raise_for_status()
        rows = resp.json()["data"]

        df = pd.DataFrame(rows, columns=["date", "close"])
        df["date"] = pd.to_datetime(df["date"], unit="ms")
        df = df.set_index("date")
        df.index = df.index.normalize()
        df.index.name = "date"
        df = df.sort_index(ascending=False)
        return df

    def market_cap(self, frequency: Frequency = "annual") -> pd.DataFrame:
        """
        Historical market cap.

        Args:
            frequency: One of "daily", "weekly", "monthly", "quarterly", "annual".

        Returns a DataFrame with columns: date, marketCap.
        """
        node_data = fetch_data_json(f"/stocks/{self._symbol}/market-cap")
        meta = node_data[0]
        tables = resolve(meta["tables"], node_data)
        rows = tables.get(frequency, [])

        if not isinstance(rows, list):
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        df = df.rename(columns={"d": "date", "p": "percent_change", "v": "value"})
        if "date" in df.columns:
            df = df.set_index("date")
            df.index.name = "date"
        return df
