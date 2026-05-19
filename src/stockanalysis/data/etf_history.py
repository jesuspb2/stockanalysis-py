from __future__ import annotations

import pandas as pd

from stockanalysis.core.http import fetch_data_json, resolve


class ETFHistory:
    """Historical price and AUM data for an ETF."""

    def __init__(self, symbol: str) -> None:
        self._symbol = symbol.lower()

    def prices(self) -> pd.DataFrame:
        """Daily OHLCV price history."""
        node_data = fetch_data_json(f"/etf/{self._symbol}/history")
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
        if "date" in df.columns:
            df = df.set_index("date")
        return df
