from stockanalysis.core.http import clear_cache
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


__all__ = ["stock", "Stock", "clear_cache"]
