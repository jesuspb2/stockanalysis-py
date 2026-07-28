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
        params = {"p": "quarterly"} if period == "quarterly" else {}
        node_data = fetch_data_json(path, params)
        df = extract_financial_df(node_data)
        if period == "annual":
            df = df[df.index != "TTM"]
        return df

    def income_statement(self, period: Period = "annual") -> pd.DataFrame:
        """Income statement (revenue, gross profit, net income, EPS, EBITDA…)."""
        # `/financials` used to serve the income statement. It is now a summary page
        # built from `sections` with no top-level `financialData`, so the income
        # statement lives at its own path. The dedicated path also returns more
        # columns than the old one (ebitda, rnd, sharesBasic…).
        df = self._fetch("financials/income-statement", period)
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

    def kpis(self, period: Period = "annual") -> pd.DataFrame:
        """Key financial KPIs by category (revenue, gross profit, margins…)."""
        path = f"/stocks/{self._symbol}/financials/metrics"
        params = {"p": "quarterly"} if period == "quarterly" else {}
        node_data = fetch_data_json(path, params)
        df = extract_metrics_df(node_data)
        if period == "annual":
            df = df[df.index != "TTM"]
        return df
