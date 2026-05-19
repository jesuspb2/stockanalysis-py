# stockanalysis-py

Python library for extracting financial data from [stockanalysis.com](https://stockanalysis.com). Returns clean `pandas` DataFrames with no API key required.

## Installation

```bash
pip install git+https://github.com/jesuspb2/stockanalysis-py.git
```

With the optional Pro authentication support:

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

Authentication unlocks the full historical data for `forecasts.recommendations()` (~1 year without auth vs. the complete multi-year history with auth). Other forecast endpoints (`estimates`, `revenue`, `eps`, `price_targets`) return complete data without authentication.

```bash
# 1. Add credentials to .env
SA_EMAIL=you@example.com
SA_PASSWORD=yourpassword

# 2. Save session (runs a headless browser login once)
uv run stockanalysis-login
```

The session is stored in `.auth/state.json` and reused automatically on subsequent calls.

---

## Stocks

```python
import stockanalysis as sa

stock = sa.stock("AAPL")
```

### `stock.financials`

| Method | Description | Returns |
|---|---|---|
| `income_statement(period="annual")` | Revenue, gross profit, net income, EPS, EBITDA… | `DataFrame` |
| `balance_sheet(period="annual")` | Assets, liabilities, equity… | `DataFrame` |
| `cash_flow(period="annual")` | Operating, investing, and financing cash flows | `DataFrame` |
| `kpis(period="annual")` | Key financial KPIs grouped by category | `DataFrame` |

`period` accepts `"annual"` or `"quarterly"`.

```python
stock.financials.income_statement()
stock.financials.income_statement(period="quarterly")
stock.financials.balance_sheet()
stock.financials.cash_flow(period="quarterly")
stock.financials.kpis()
```

### `stock.forecasts`

| Method | Description | Returns |
|---|---|---|
| `estimates(period="annual")` | Consensus revenue, EPS, EBITDA, net income… | `DataFrame` |
| `revenue(period="annual")` | Revenue estimates only | `Series` |
| `eps(period="annual")` | EPS estimates only | `Series` |
| `price_targets()` | High, low, average, median, current price targets, and analyst count | `dict` |
| `recommendations()` | Buy/hold/sell breakdown over time | `DataFrame` |

`period` accepts `"annual"` or `"quarterly"`.

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
# DataFrame with columns: strongBuy, buy, hold, sell, strongSell
```

### `stock.history`

| Method | Description | Returns |
|---|---|---|
| `prices()` | Daily OHLCV price history | `DataFrame` |
| `market_cap(frequency="annual")` | Historical market cap | `DataFrame` |

`frequency` accepts `"daily"`, `"weekly"`, `"monthly"`, `"quarterly"`, or `"annual"`.

```python
stock.history.prices()
# DataFrame indexed by date with columns: open, high, low, close, volume, change

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
# {"name": "Apple Inc.", "sector": "Technology", "ceo": "Tim Cook", ...}

stock.company.description()
stock.company.executives()
```

### `stock.dividend`

| Method | Description | Returns |
|---|---|---|
| `info()` | Current dividend yield, frequency, next payment date… | `str` |
| `history()` | Full payment history indexed by ex-dividend date | `DataFrame` |

```python
stock.dividend.info()
stock.dividend.history()
# DataFrame with columns: amount, type, declarationDate, recordDate, paymentDate
```

### `stock.employees`

| Method | Description | Returns |
|---|---|---|
| `history()` | Headcount history | `DataFrame` |

```python
stock.employees.history()
# DataFrame with columns: count, change, growth
```

### `stock.metrics`

Segment-level breakdowns. `period` accepts `"quarterly"` or `"trailing"` (`"annual"` is accepted as an alias for `"trailing"`).

| Method | Description | Returns |
|---|---|---|
| `revenue_by_segment(period="quarterly")` | Revenue by product/service segment | `DataFrame` |
| `gross_profit_by_type(period="quarterly")` | Gross profit by segment type | `DataFrame` |
| `gross_margin_by_type(period="quarterly")` | Gross margin (%) by segment type | `DataFrame` |
| `revenue_by_geography(period="quarterly")` | Revenue by geography | `DataFrame` |
| `operating_expense_breakdown(period="quarterly")` | OpEx by category | `DataFrame` |
| `operating_metrics()` | Annual operating metrics unique to the company (e.g. active devices) | `DataFrame` |

```python
stock.metrics.revenue_by_segment()
stock.metrics.revenue_by_geography(period="trailing")
stock.metrics.operating_metrics()
```

> Not all metrics are available for every ticker — availability depends on what stockanalysis.com reports for that company.

### Direct methods on `Stock`

| Method | Description | Returns |
|---|---|---|
| `ratios(period="annual")` | P/E, P/S, EV/EBITDA, margins, and more | `DataFrame` |
| `statistics()` | All valuation stats as a flat table (section, id, title, value) | `DataFrame` |
| `overview()` | Price metrics, analyst rating, description from the main page | `dict` |
| `transcripts()` | Earnings call transcript list with date, quarter, summary, audio URL | `DataFrame` |
| `transcript(id)` | Structured transcript with AI summary and speaker turns | `dict` |

```python
stock.ratios()
stock.ratios(period="quarterly")

stock.statistics()
stock.overview()

transcripts = stock.transcripts()
# DataFrame columns: id, date, quarter, fiscal_year, title, summary, audio_url

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
| `overview()` | AUM, expense ratio, description, fund info | `dict` |
| `holdings(top=None)` | Full holdings list; pass `top=N` to limit | `DataFrame` |
| `sectors()` | Sector allocation with weights | `DataFrame` |
| `performance()` | Returns by period: 1m, 3m, 6m, YTD, 1y, 3y, 5y, 10y | `DataFrame` |
| `history.prices()` | Daily OHLCV price history | `DataFrame` |

```python
etf.overview()
etf.holdings()
etf.holdings(top=10)
etf.sectors()
# DataFrame with columns: sector, weight

etf.performance()
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

### `sa.screener(...)`

Filter stocks by fundamental criteria.

| Parameter | Type | Description |
|---|---|---|
| `market_cap_min` | `float` | Minimum market cap in USD (e.g. `10e9` for $10B) |
| `market_cap_max` | `float` | Maximum market cap in USD |
| `sector` | `str` | Sector name (e.g. `"Technology"`, `"Healthcare"`) |
| `country` | `str` | Country code (e.g. `"US"`, `"CN"`) |
| `exchange` | `str` | Exchange (e.g. `"NYSE"`, `"NASDAQ"`) |

Returns a `DataFrame` with columns: `symbol`, `name`, `marketCap`, `price`, `change`, `revenue`, `netIncome`, `peRatio`, `sector`.

```python
sa.screener(sector="Technology", market_cap_min=10e9)
sa.screener(sector="Healthcare", country="US", exchange="NYSE")
sa.screener(market_cap_min=1e9, market_cap_max=10e9)
```

---

## Cache

HTTP responses are cached in-session to avoid duplicate requests. Call `clear_cache()` to reset between runs in a long-lived process.

```python
sa.clear_cache()
```

---

## License

MIT
