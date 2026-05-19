from __future__ import annotations

import pandas as pd

from stockanalysis.core.http import fetch_data_json, resolve


class Employees:
    """Historical employee count data."""

    def __init__(self, symbol: str) -> None:
        self._symbol = symbol.lower()

    def history(self) -> pd.DataFrame:
        """
        Historical annual employee headcount.

        Returns a DataFrame indexed by date with columns: count, change, growth.
        """
        node_data = fetch_data_json(f"/stocks/{self._symbol}/employees")
        meta = node_data[0]
        rows = resolve(meta["historical_annual"], node_data)

        if not isinstance(rows, list) or len(rows) == 0:
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        df = df.drop(columns=[c for c in ("fullTime", "partTime") if c in df.columns])
        if "date" in df.columns:
            df = df.set_index("date")
            df.index.name = "date"
        return df
