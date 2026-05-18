from __future__ import annotations

import pandas as pd

from stockanalysis.data.etf_history import ETFHistory
from stockanalysis.data.etf_holdings import ETFHoldings
from stockanalysis.data.etf_overview import (
    fetch_etf_overview,
    fetch_etf_performance,
    fetch_etf_sectors,
)


class ETF:
    """
    Entry point for stockanalysis.com ETF data for a single fund.

    Usage:
        import stockanalysis as sa

        spy = sa.etf("SPY")

        spy.overview()            # AUM, expense ratio, description, fund info…
        spy.holdings()            # full holdings list as DataFrame
        spy.holdings(top=10)      # top 10 holdings
        spy.sectors()             # sector allocation DataFrame
        spy.performance()         # returns by period (1m, 3m, YTD, 1y…)
        spy.history.prices()      # daily OHLCV price history
    """

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol.upper()
        self._sym = symbol.lower()
        self.holdings = ETFHoldings(symbol)
        self.history = ETFHistory(symbol)

    def overview(self) -> dict:
        """AUM, expense ratio, description, and key fund info."""
        return fetch_etf_overview(self._sym)

    def sectors(self) -> pd.DataFrame:
        """Sector allocation as a DataFrame with columns: sector, weight."""
        return fetch_etf_sectors(self._sym)

    def performance(self) -> pd.DataFrame:
        """Returns by period (1m, 3m, 6m, YTD, 1y, 3y, 5y, 10y)."""
        return fetch_etf_performance(self._sym)

    def __repr__(self) -> str:
        return f"ETF('{self.symbol}')"
