from __future__ import annotations

import pandas as pd

from stockanalysis.core.http import fetch_data_json, parse_numeric, resolve


class ETFHoldings:
    """ETF holdings data."""

    def __init__(self, symbol: str) -> None:
        self._symbol = symbol.lower()

    def __call__(self, top: int | None = None) -> pd.DataFrame:
        """Full holdings list. Pass top=N to limit to the N largest positions."""
        node_data = fetch_data_json(f"/etf/{self._symbol}/holdings")
        meta = node_data[0]
        rows = resolve(meta.get("holdings", 0), node_data)
        if not isinstance(rows, list):
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        df = df.rename(
            columns={
                "no": "rank",
                "n": "name",
                "s": "symbol",
                "as": "weight_pct",
                "sh": "shares",
            }
        )
        if "weight_pct" in df.columns:
            df["weight_pct"] = df["weight_pct"].map(parse_numeric)
        if top is not None:
            df = df.head(top)
        return df
