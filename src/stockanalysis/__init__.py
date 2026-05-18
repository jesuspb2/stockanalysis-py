from stockanalysis.core.http import clear_cache
from stockanalysis.data.search import screener, search
from stockanalysis.etf import ETF
from stockanalysis.stock import Stock


def stock(symbol: str) -> Stock:
    """
    Create a Stock object for the given ticker symbol.

    Usage:
        import stockanalysis as sa

        aapl = sa.stock("AAPL")
        aapl.financials.income_statement()
        aapl.financials.balance_sheet(period="quarterly")
        aapl.ratios()
        aapl.transcripts()
        aapl.transcript(12345)

        sa.clear_cache()  # flush in-session HTTP cache
    """
    return Stock(symbol)


def etf(symbol: str) -> ETF:
    """
    Create an ETF object for the given ticker symbol.

    Usage:
        import stockanalysis as sa

        spy = sa.etf("SPY")
        spy.overview()
        spy.holdings()
        spy.holdings(top=10)
        spy.sectors()
        spy.performance()
        spy.history.prices()
    """
    return ETF(symbol)


__all__ = ["stock", "Stock", "etf", "ETF", "search", "screener", "clear_cache"]
