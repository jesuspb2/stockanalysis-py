from __future__ import annotations

from typing import Literal

import pandas as pd

from stockanalysis.core.http import fetch_data_json, resolve

Frequency = Literal["daily", "weekly", "monthly", "quarterly", "annual"]


class History:
    """Historical price data and market cap history."""

    def __init__(self, symbol: str) -> None:
        self._symbol = symbol.lower()

    def prices(self) -> pd.DataFrame:
        """
        Daily OHLCV price history.

        Returns a DataFrame indexed by date with columns:
        open, high, low, close, volume, change (%).
        """
        node_data = fetch_data_json(f"/stocks/{self._symbol}/history")
        meta = node_data[0]
        raw = resolve(meta["data"], node_data)
        rows = resolve(raw.get("data", []), node_data)

        if not isinstance(rows, list):
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        df = df.rename(
            columns={
                "t": "date",
                "o": "open",
                "h": "high",
                "l": "low",
                "c": "close",
                "v": "volume",
                "ch": "change",
                "a": "adjusted_close",
                "div": "dividend",
            }
        )
        df = df.set_index("date")
        df.index.name = "date"
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
        if "date" in df.columns:
            df = df.set_index("date")
            df.index.name = "date"
        return df
