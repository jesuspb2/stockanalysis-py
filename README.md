# stockanalysis-py

Python library for extracting financial data from [stockanalysis.com](https://stockanalysis.com). Returns clean `pandas` DataFrames — no API key required.

## Installation

```bash
pip install git+https://github.com/jesuspb2/stockanalysis-py.git
```

With optional Pro authentication support (unlocks extended historical data):

```bash
pip install "stockanalysis-py[auth] @ git+https://github.com/jesuspb2/stockanalysis-py.git"
```

## Quick start

```python
import stockanalysis as sa

# Stocks
aapl = sa.stock("AAPL")
aapl.financials.income_statement()
aapl.forecasts.estimates()
aapl.history.prices()

# ETFs
spy = sa.etf("SPY")
spy.holdings(top=10)
spy.performance()

# Search & screen
sa.search("Apple")
sa.screener(sector="Technology", market_cap_min=10e9)
```

---

## Authentication (Pro)

Authentication unlocks extended historical data for certain endpoints. For example, `forecasts.recommendations()` returns ~1 year of data without auth and the full multi-year history with auth. All other endpoints return complete data without authentication.

```bash
# 1. Add credentials to .env at the project root
SA_EMAIL=you@example.com
SA_PASSWORD=yourpassword

# 2. Save session once (runs a headless browser login)
stockanalysis-login
```

The session is stored in `.auth/state.json` and reused automatically on all subsequent requests.

---

## Stocks

```python
import stockanalysis as sa

stock = sa.stock("AAPL")
```

### `stock.financials`

Financial statement data. `period` accepts `"annual"` (default) or `"quarterly"`.

| Method | Description | Returns |
|---|---|---|
| `income_statement(period="annual")` | Revenue, gross profit, net income, EPS, EBITDA… | `DataFrame` |
| `balance_sheet(period="annual")` | Assets, liabilities, equity… | `DataFrame` |
| `cash_flow(period="annual")` | Operating, investing, and financing cash flows | `DataFrame` |
| `kpis(period="annual")` | Key financial KPIs grouped by category | `DataFrame` |

```python
stock.financials.income_statement()
stock.financials.income_statement(period="quarterly")
stock.financials.balance_sheet()
stock.financials.cash_flow(period="quarterly")
stock.financials.kpis()
```

### `stock.forecasts`

Analyst estimates and price targets. `period` accepts `"annual"` (default) or `"quarterly"`.

| Method | Description | Returns |
|---|---|---|
| `estimates(period="annual")` | Consensus revenue, EPS, EBITDA, net income… | `DataFrame` |
| `revenue(period="annual")` | Revenue estimates only | `Series` |
| `eps(period="annual")` | EPS estimates only | `Series` |
| `price_targets()` | High, low, average, median, current price, and analyst count | `dict` |
| `recommendations()` | Buy/hold/sell breakdown over time | `DataFrame` |

```python
stock.forecasts.estimates()
stock.forecasts.estimates(period="quarterly")
stock.forecasts.revenue()
stock.forecasts.eps()

stock.forecasts.price_targets()
# {
#   "high": 250.0,
#   "low": 160.0,
#   "average": 210.0,
#   "median": 212.0,
#   "current": 195.0,
#   "num_price_targets": 37,
# }

stock.forecasts.recommendations()
# DataFrame indexed by date with columns: strongBuy, buy, hold, sell, strongSell
```

### `stock.history`

| Method | Description | Returns |
|---|---|---|
| `prices()` | Daily OHLCV price history | `DataFrame` |
| `market_cap(frequency="annual")` | Historical market cap | `DataFrame` |

`frequency` accepts `"daily"`, `"weekly"`, `"monthly"`, `"quarterly"`, or `"annual"`.

```python
stock.history.prices()
# DataFrame indexed by date:
#             open    high     low   close      volume  change
# date
# 2020-01-02  296.24  300.60  295.19  300.35  33870100    0.012

stock.history.market_cap()
stock.history.market_cap(frequency="monthly")
```

### `stock.company`

| Method | Description | Returns |
|---|---|---|
| `profile()` | Name, sector, industry, country, CEO, IPO date, founded year, employees | `dict` |
| `description()` | Long-form business description | `str` |
| `executives()` | Key executives — name and title | `DataFrame` |

```python
stock.company.profile()
# {
#   "name": "Apple Inc.",
#   "sector": "Technology",
#   "industry": "Consumer Electronics",
#   "country": "US",
#   "ceo": "Tim Cook",
#   "ipoDate": "1980-12-12",
#   "founded": 1976,
#   "employees": 161000,
# }

stock.company.description()
stock.company.executives()
# DataFrame with columns: name, title
```

### `stock.dividend`

| Method | Description | Returns |
|---|---|---|
| `info()` | Current dividend amount, yield, frequency, dates, payout ratio | `dict` |
| `history()` | Full payment history indexed by ex-dividend date | `DataFrame` |

```python
stock.dividend.info()
# {
#   "annual_amount": 1.0,
#   "yield_pct": 0.51,
#   "frequency": "Quarterly",
#   "ex_date": "2025-02-07",
#   "pay_date": "2025-02-13",
#   "payout_ratio": 15.2,
#   "summary": "Apple pays a quarterly dividend of $0.25 per share.",
# }

stock.dividend.history()
# DataFrame indexed by ex_date with columns:
# amount, type, declaration_date, record_date, payment_date
```

### `stock.employees`

| Method | Description | Returns |
|---|---|---|
| `history()` | Annual employee headcount over time | `DataFrame` |

```python
stock.employees.history()
# DataFrame indexed by date with columns: count, change, growth
```

### `stock.metrics`

Segment-level breakdowns. `period` accepts `"quarterly"` (default), `"trailing"`, or `"annual"` (alias for `"trailing"`).

| Method | Description | Returns |
|---|---|---|
| `revenue_by_segment(period="quarterly")` | Revenue by product/service segment | `DataFrame` |
| `gross_profit_by_type(period="quarterly")` | Gross profit by segment type | `DataFrame` |
| `gross_margin_by_type(period="quarterly")` | Gross margin (%) by segment type | `DataFrame` |
| `revenue_by_geography(period="quarterly")` | Revenue by geography | `DataFrame` |
| `operating_expense_breakdown(period="quarterly")` | OpEx by category | `DataFrame` |
| `operating_metrics()` | Company-specific operating metrics (e.g. active devices, subscribers) | `DataFrame` |

```python
stock.metrics.revenue_by_segment()
stock.metrics.revenue_by_geography(period="trailing")
stock.metrics.operating_metrics()
```

> Not all metrics are available for every ticker — availability depends on what stockanalysis.com reports for that company.

### Direct methods on `Stock`

| Method | Description | Returns |
|---|---|---|
| `overview()` | Price, market cap, P/E, analyst rating, earnings date from the main page | `dict` |
| `ratios(period="annual")` | P/E, P/S, EV/EBITDA, margins, and more | `DataFrame` |
| `statistics()` | All valuation stats as a flat table — section, id, title, value | `DataFrame` |
| `transcripts()` | Earnings call transcript list with date, quarter, summary, audio URL | `DataFrame` |
| `transcript(id)` | Full transcript with AI summary and speaker turns | `dict` |

```python
stock.overview()
# {
#   "marketCap": 3_000_000_000_000,
#   "revenue": 395_000_000_000,
#   "netIncome": 94_000_000_000,
#   "eps": 6.11,
#   "peRatio": 32.1,
#   "forwardPE": 28.5,
#   "dividend": "$1.00",
#   "exDividendDate": "2025-02-07",
#   "beta": 1.24,
#   "analysts": "Buy",
#   "target": 230.0,
#   "earningsDate": "2025-05-01",
#   "description": "Apple Inc. designs...",
# }

stock.ratios()
stock.ratios(period="quarterly")

stock.statistics()
# DataFrame with columns: section, id, title, value
# Sections: valuation, shares, ratios, evRatios, financialPosition,
#           financialEfficiency, taxes, stockPrice, shortSelling,
#           incomeStatement, balanceSheet, cashFlow, margins,
#           dividends, analystForecasts, stockSplits, scores, fairValue

transcripts = stock.transcripts()
# DataFrame with columns: id, date, quarter, fiscal_year, title, summary, audio_url

transcript_id = transcripts.iloc[0]["id"]
stock.transcript(transcript_id)
# {
#   "title": "Apple Q2 2026 Earnings Call",
#   "summary_html": "<p>AI-generated summary...</p>",
#   "turns": [
#     {"speaker": "Tim Cook", "role": "CEO", "text": "..."},
#   ],
# }
```

---

## ETFs

```python
import stockanalysis as sa

etf = sa.etf("SPY")
```

| Method | Description | Returns |
|---|---|---|
| `overview()` | AUM, expense ratio, NAV, inception date, category, issuer, and more | `dict` |
| `holdings(top=None)` | Full holdings list; pass `top=N` to limit to N largest positions | `DataFrame` |
| `sectors()` | Sector allocation with weights | `DataFrame` |
| `performance()` | Returns by period: 1m, YTD, 1y, 3y CAGR, 5y CAGR, 10y CAGR, max CAGR | `DataFrame` |
| `history.prices()` | Daily OHLCV price history | `DataFrame` |

```python
etf.overview()
# {
#   "description": "...",
#   "expenseRatio": 0.0945,
#   "aum": 537_000_000_000,
#   "nav": 524.12,
#   "inceptionDate": "1993-01-22",
#   "index": "S&P 500",
#   "category": "Large Blend",
#   "issuer": "State Street",
#   "assetClass": "Equity",
#   "numHoldings": 503,
#   "dividend": "$6.55",
#   "dividendYield": 1.25,
#   "pe": 22.4,
#   "beta": 1.0,
# }

etf.holdings()          # all holdings
etf.holdings(top=10)    # top 10 by weight
# DataFrame with columns: rank, name, symbol, weight_pct, shares

etf.sectors()
# DataFrame with columns: sector, weight

etf.performance()
# DataFrame with columns: period, return
# Periods: 1m, YTD, 1y, 3y_cagr, 5y_cagr, 10y_cagr, max_cagr

etf.history.prices()
# DataFrame indexed by date with columns: open, high, low, close, volume, change
```

---

## Search & Screener

### `sa.search(query)`

Search for stocks, ETFs, and indices by name or ticker.

```python
results = sa.search("Apple")
# [{"symbol": "AAPL", "name": "Apple Inc.", "type": "stock"}, ...]
```

Returns a list of dicts with keys: `symbol`, `name`, `type` (`"stock"`, `"etf"`, or `"index"`).

### `sa.screener(...)`

Filter stocks by fundamental criteria.

| Parameter | Type | Description |
|---|---|---|
| `market_cap_min` | `float` | Minimum market cap in USD (e.g. `10e9` for $10B) |
| `market_cap_max` | `float` | Maximum market cap in USD |
| `sector` | `str` | One of the 11 GICS sectors (see below) |
| `country` | `str` | Country code (e.g. `"US"`, `"CN"`, `"GB"`) |
| `exchange` | `str` | Exchange (e.g. `"NYSE"`, `"NASDAQ"`) |
| `**extra_params` | `str` | Additional raw filter params passed directly to the endpoint |

Returns a `DataFrame` with columns: `symbol`, `name`, `marketCap`, `price`, `change`, `industry`, `peRatio`.

Valid sectors (11 GICS sectors):

```
"Communication Services"   "Consumer Discretionary"   "Consumer Staples"
"Energy"                   "Financials"                "Healthcare"
"Industrials"              "Materials"                 "Real Estate"
"Technology"               "Utilities"
```

```python
sa.screener(sector="Technology", market_cap_min=10e9)
sa.screener(sector="Healthcare", country="US", exchange="NYSE")
sa.screener(market_cap_min=2e9, market_cap_max=10e9)
```

---

## Cache

HTTP responses are cached in-session to avoid duplicate requests. Call `clear_cache()` to reset between runs in a long-lived process (e.g. a Jupyter notebook session).

```python
sa.clear_cache()
```

---

## License

MIT
