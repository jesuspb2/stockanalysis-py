from stockanalysis.core.http import clear_cache
from stockanalysis.data.news import fetch_market_news
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


def news(category: str = "markets"):
    """General stock market news feed.

    Args:
        category: "markets" (default), "all-stocks", or "press-releases".

    Returns a DataFrame with columns:
        time, ago, title, text, source, type, tickers, url, img

    Usage:
        sa.news()                    # market headlines
        sa.news("all-stocks")        # all stock-specific news
        sa.news("press-releases")    # press releases
    """
    return fetch_market_news(category)


__all__ = ["stock", "Stock", "etf", "ETF", "news", "search", "screener", "clear_cache"]
