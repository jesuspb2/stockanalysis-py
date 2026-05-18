from __future__ import annotations

from typing import Literal

import pandas as pd

from stockanalysis.core.http import fetch_data_json, resolve

Period = Literal["annual", "quarterly"]


class Employees:
    """Historical employee count data."""

    def __init__(self, symbol: str) -> None:
        self._symbol = symbol.lower()

    def history(self, period: Period = "annual") -> pd.DataFrame:
        """
        Historical employee headcount.

        Args:
            period: "annual" or "quarterly".

        Returns a DataFrame indexed by date with columns:
        count, change, growth, fullTime, partTime.
        """
        node_data = fetch_data_json(f"/stocks/{self._symbol}/employees")
        meta = node_data[0]
        key = "historical_annual" if period == "annual" else "historical_quarterly"
        rows = resolve(meta[key], node_data)

        if not isinstance(rows, list):
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        if "date" in df.columns:
            df = df.set_index("date")
            df.index.name = "date"
        return df
