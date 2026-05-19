from __future__ import annotations

from typing import Literal

import pandas as pd

from stockanalysis.core.http import (
    fetch_data_json,
    extract_financial_df,
    extract_metrics_df,
)

Period = Literal["annual", "quarterly"]


class Financials:
    """Financial statement data for a stock."""

    def __init__(self, symbol: str) -> None:
        self._symbol = symbol.lower()

    def _fetch(self, path_suffix: str, period: Period) -> pd.DataFrame:
        path = f"/stocks/{self._symbol}/{path_suffix}"
        params = {} if period == "annual" else {"p": "quarterly"}
        node_data = fetch_data_json(path, params)
        return extract_financial_df(node_data)

    def income_statement(self, period: Period = "annual") -> pd.DataFrame:
        """Income statement (revenue, gross profit, net income, EPS, EBITDA…)."""
        df = self._fetch("financials", period)
        return df.rename(
            columns={
                "cor": "cost_of_revenue",
                "sgna": "sga_expense",
                "rnd": "rd_expense",
            }
        )

    def balance_sheet(self, period: Period = "annual") -> pd.DataFrame:
        """Balance sheet (assets, liabilities, equity…)."""
        return self._fetch("financials/balance-sheet", period)

    def cash_flow(self, period: Period = "annual") -> pd.DataFrame:
        """Cash flow statement (operating, investing, financing…)."""
        return self._fetch("financials/cash-flow-statement", period)

    def metrics(self, period: Period = "annual") -> pd.DataFrame:
        """Key financial metrics by category (revenue, gross profit, KPIs…)."""
        path = f"/stocks/{self._symbol}/financials/metrics"
        params = {} if period == "annual" else {"p": "quarterly"}
        node_data = fetch_data_json(path, params)
        return extract_metrics_df(node_data)
