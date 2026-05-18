from __future__ import annotations

import pandas as pd

from stockanalysis.core.http import fetch_data_json, resolve

_SECTIONS = [
    "valuation", "shares", "ratios", "evRatios", "financialPosition",
    "financialEfficiency", "taxes", "stockPrice", "shortSelling",
    "incomeStatement", "balanceSheet", "cashFlow", "margins",
    "dividends", "analystForecasts", "stockSplits", "scores", "fairValue",
]


class Statistics:
    """Valuation, ratios, and key stats snapshot for a stock."""

    def __init__(self, symbol: str) -> None:
        self._symbol = symbol.lower()

    def _fetch(self) -> tuple[list, dict]:
        node_data = fetch_data_json(f"/stocks/{self._symbol}/statistics")
        return node_data, node_data[0]

    def all(self) -> dict[str, list[dict]]:
        """
        All statistics sections as a dict of lists.

        Each section is a list of {id, title, value, ...} dicts.
        Keys: valuation, shares, ratios, evRatios, financialPosition,
              financialEfficiency, taxes, stockPrice, shortSelling,
              incomeStatement, balanceSheet, cashFlow, margins,
              dividends, analystForecasts, stockSplits, scores, fairValue.
        """
        node_data, meta = self._fetch()
        return {
            section: resolve(meta[section], node_data).get("data", [])
            for section in _SECTIONS
            if section in meta
        }

    def to_dataframe(self) -> pd.DataFrame:
        """
        All statistics as a single DataFrame with columns:
        section, id, title, value.
        """
        rows = []
        for section, items in self.all().items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        rows.append({
                            "section": section,
                            "id": item.get("id"),
                            "title": item.get("title"),
                            "value": item.get("value"),
                        })
        return pd.DataFrame(rows)
