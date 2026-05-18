from __future__ import annotations

import pandas as pd

from stockanalysis.core.http import fetch_data_json, resolve


class Dividend:
    """Dividend history and summary information."""

    def __init__(self, symbol: str) -> None:
        self._symbol = symbol.lower()

    def _fetch(self) -> tuple[list, dict]:
        node_data = fetch_data_json(f"/stocks/{self._symbol}/dividend")
        return node_data, node_data[0]

    def info(self) -> str:
        """Plain-text summary of the current dividend (yield, frequency, next date…)."""
        node_data, meta = self._fetch()
        return resolve(meta["infoBox"], node_data)

    def history(self) -> pd.DataFrame:
        """
        Full dividend payment history.

        Returns a DataFrame indexed by ex-dividend date with columns:
        amount, type, declaration date, record date, payment date.
        """
        node_data, meta = self._fetch()
        rows = resolve(meta["history"], node_data)

        if not isinstance(rows, list):
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        date_col = next((c for c in ("exDate", "ex_date", "date") if c in df.columns), None)
        if date_col:
            df = df.set_index(date_col)
            df.index.name = "ex_date"
        return df
