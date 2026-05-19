# stockanalysis-py

Python library for extracting financial data from [stockanalysis.com](https://stockanalysis.com). Returns clean `pandas` DataFrames — no API key required.

## What it does

**stockanalysis-py** wraps the stockanalysis.com website data into a simple Python API. You can pull full financial statements, analyst forecasts, price history, earnings call transcripts, ETF holdings, and more — all as structured DataFrames — without registering for any API key.

## Feature overview

| Area | What you get |
|---|---|
| **[Stocks](stocks.md)** | Financials (income statement, balance sheet, cash flow, KPIs), analyst forecasts (estimates, price targets, recommendations), price history, market cap history, company profile, dividends, employee headcount, segment metrics, valuation statistics, earnings call transcripts |
| **[ETFs](etfs.md)** | Holdings (full list or top N), sector allocation, performance returns by period, price history, fund overview (AUM, expense ratio, NAV, category, issuer) |
| **[Search & Screener](search-screener.md)** | Search by name or ticker symbol; filter stocks by sector, market cap range, country, and exchange |

## Quick start

```python
import stockanalysis as sa

# --- Stocks ---
aapl = sa.stock("AAPL")

aapl.financials.income_statement()           # annual income statement
aapl.financials.income_statement("quarterly") # quarterly
aapl.financials.balance_sheet()
aapl.financials.cash_flow()
aapl.financials.kpis()

aapl.forecasts.estimates()                   # consensus revenue, EPS, EBITDA…
aapl.forecasts.price_targets()               # high/low/average/median targets
aapl.forecasts.recommendations()             # buy/hold/sell over time

aapl.history.prices()                        # daily OHLCV
aapl.history.market_cap(frequency="monthly") # monthly market cap

aapl.company.profile()                       # sector, industry, CEO, IPO date…
aapl.company.description()                   # long-form business description
aapl.company.executives()                    # name + title DataFrame

aapl.dividend.info()                         # yield, frequency, next payment date
aapl.dividend.history()                      # full payment history

aapl.employees.history()                     # headcount over time

aapl.metrics.revenue_by_segment()            # revenue by product line
aapl.metrics.revenue_by_geography()          # revenue by region
aapl.metrics.operating_metrics()             # company-specific KPIs

aapl.overview()                              # price, P/E, analyst rating
aapl.ratios()                                # P/E, EV/EBITDA, margins…
aapl.statistics()                            # all valuation stats as flat table

transcripts = aapl.transcripts()             # list of earnings calls
aapl.transcript(transcripts.iloc[0]["id"])   # full transcript with AI summary

# --- ETFs ---
spy = sa.etf("SPY")

spy.overview()                               # AUM, expense ratio, NAV…
spy.holdings(top=10)                         # top 10 holdings by weight
spy.sectors()                                # sector allocation
spy.performance()                            # returns: 1m, YTD, 1y, 3y CAGR…
spy.history.prices()                         # daily OHLCV

# --- Search & Screener ---
sa.search("Apple")                           # search by name or ticker
sa.screener(sector="Technology", market_cap_min=10e9)
```

## Installation

```bash
pip install git+https://github.com/jesuspb2/stockanalysis-py.git
```

See the [Installation](installation.md) page for full details including optional Pro authentication support.
