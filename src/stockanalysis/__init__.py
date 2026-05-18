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
    """
    return Stock(symbol)


__all__ = ["stock", "Stock"]
