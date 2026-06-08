from __future__ import annotations

from typing import Any, Literal

import pandas as pd

from stockanalysis.core.http import fetch_data_json, extract_financial_df
from stockanalysis.data.company import Company
from stockanalysis.data.dividend import Dividend
from stockanalysis.data.employees import Employees
from stockanalysis.data.financials import Financials
from stockanalysis.data.forecast import Forecasts
from stockanalysis.data.history import History
from stockanalysis.data.metrics import Metrics
from stockanalysis.data.overview import fetch_overview
from stockanalysis.data.statistics import Statistics
from stockanalysis.data.news import fetch_news
from stockanalysis.data.transcripts import fetch_transcript, fetch_transcripts

Period = Literal["annual", "quarterly"]


class Stock:
    """
    Entry point for stockanalysis.com data for a single ticker.

    Usage:
        import stockanalysis as sa

        stock = sa.stock("AAPL")

        # Namespaced
        stock.financials.income_statement(period="annual")
        stock.financials.balance_sheet(period="quarterly")
        stock.financials.cash_flow()
        stock.financials.kpis()
        stock.forecasts.estimates()
        stock.forecasts.revenue()
        stock.forecasts.eps()
        stock.forecasts.price_targets()
        stock.forecasts.recommendations()
        stock.history.prices()
        stock.history.market_cap(frequency="annual")
        stock.company.profile()
        stock.company.description()
        stock.company.executives()
        stock.dividend.info()
        stock.dividend.history()
        stock.employees.history(period="annual")
        stock.metrics.revenue_by_segment()
        stock.metrics.gross_profit_by_type()
        stock.metrics.gross_margin_by_type()
        stock.metrics.revenue_by_geography()
        stock.metrics.operating_expense_breakdown()

        # Direct methods
        stock.ratios(period="annual")
        stock.statistics()
        stock.overview()
        stock.transcripts()
        stock.transcript(12345)
    """

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol.upper()
        self.financials = Financials(symbol)
        self.forecasts = Forecasts(symbol)
        self.history = History(symbol)
        self.company = Company(symbol)
        self.dividend = Dividend(symbol)
        self.employees = Employees(symbol)
        self.metrics = Metrics(symbol)

    def ratios(self, period: Period = "annual") -> pd.DataFrame:
        """Key financial ratios (P/E, P/S, EV/EBITDA, margins…)."""
        path = f"/stocks/{self.symbol.lower()}/financials/ratios"
        params = {"p": "quarterly"} if period == "quarterly" else {}
        df = extract_financial_df(fetch_data_json(path, params))
        if period == "annual":
            df = df[df.index != "TTM"]
        return df

    def statistics(self) -> pd.DataFrame:
        """All valuation and key stats as a flat DataFrame (section, id, title, value)."""
        return Statistics(self.symbol).to_dataframe()

    def overview(self) -> dict[str, Any]:
        """Summary data from the main stock page (price metrics, analyst rating, description…)."""
        return fetch_overview(self.symbol)

    def news(self) -> pd.DataFrame:
        """Recent news articles for the stock."""
        return fetch_news(self.symbol)

    def transcripts(self) -> pd.DataFrame:
        """Earnings call transcript list with date, quarter, summary, and audio URL."""
        return fetch_transcripts(self.symbol)

    def transcript(self, transcript_id: int | str) -> dict[str, Any]:
        """Full text and Q&A for a single earnings call transcript by ID."""
        return fetch_transcript(self.symbol, transcript_id)

    def __repr__(self) -> str:
        return f"Stock('{self.symbol}')"
