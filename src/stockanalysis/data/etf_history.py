from __future__ import annotations

import pandas as pd

from stockanalysis.core.session import get_session

_API_BASE = "https://stockanalysis.com/api/symbol/e"


class ETFHistory:
    """Historical price and AUM data for an ETF."""

    def __init__(self, symbol: str) -> None:
        self._symbol = symbol.lower()

    def prices(self) -> pd.DataFrame:
        """Full daily close price history (from inception)."""
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
