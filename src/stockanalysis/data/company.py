from __future__ import annotations

from typing import Any, cast

import pandas as pd

from stockanalysis.core.http import fetch_data_json, resolve


class Company:
    """Company profile, executives, and description."""

    def __init__(self, symbol: str) -> None:
        self._symbol = symbol.lower()

    def _fetch(self) -> tuple[list[Any], dict[str, Any]]:
        node_data = fetch_data_json(f"/stocks/{self._symbol}/company")
        return node_data, node_data[0]

    def profile(self) -> dict[str, Any]:
        """
        Core company information: name, sector, industry, country, CEO,
        IPO date, founded year, employee count.
        """
        node_data, meta = self._fetch()
        raw = resolve(meta["profile"], node_data)
        flat: dict[str, Any] = {}
        for k, v in raw.items():
            flat[k] = v["value"] if isinstance(v, dict) and "value" in v else v
        return flat

    def description(self) -> str:
        """Long-form business description."""
        node_data, meta = self._fetch()
        return cast(str, resolve(meta["description"], node_data))

    def executives(self) -> pd.DataFrame:
        """Key executives with columns: name, title."""
        node_data, meta = self._fetch()
        rows = resolve(meta["executives"], node_data)
        if not isinstance(rows, list):
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        df.columns = [c.lower() for c in df.columns]
        return df
