# Stocks

Create a `Stock` object with `sa.stock("TICKER")` and access data through its namespaces.

```python
import stockanalysis as sa

aapl = sa.stock("AAPL")
```

The ticker is case-insensitive — `sa.stock("aapl")` and `sa.stock("AAPL")` are equivalent.

---

## `stock.financials`

Financial statement data. `period` accepts `"annual"` (default) or `"quarterly"`.

| Method | Description | Returns |
|---|---|---|
| `income_statement(period="annual")` | Revenue, gross profit, operating income, net income, EPS, EBITDA… | `DataFrame` |
| `balance_sheet(period="annual")` | Assets, liabilities, shareholder equity… | `DataFrame` |
| `cash_flow(period="annual")` | Operating, investing, and financing cash flows | `DataFrame` |
| `kpis(period="annual")` | Key financial KPIs grouped by category | `DataFrame` |

```python
aapl.financials.income_statement()
aapl.financials.income_statement(period="quarterly")
aapl.financials.balance_sheet()
aapl.financials.cash_flow(period="quarterly")
aapl.financials.kpis()
```

---

## `stock.forecasts`

Analyst estimates and price targets. `period` accepts `"annual"` (default) or `"quarterly"`.

| Method | Description | Returns |
|---|---|---|
| `estimates(period="annual")` | Consensus revenue, EPS, EBITDA, net income estimates | `DataFrame` |
| `revenue(period="annual")` | Revenue estimates only | `Series` |
| `eps(period="annual")` | EPS estimates only | `Series` |
| `price_targets()` | High, low, average, median, current price, and analyst count | `dict` |
| `recommendations()` | Buy/hold/sell breakdown over time | `DataFrame` |

```python
aapl.forecasts.estimates()
aapl.forecasts.estimates(period="quarterly")
aapl.forecasts.revenue()
aapl.forecasts.eps()

aapl.forecasts.price_targets()
# {
#   "high": 250.0,
#   "low": 160.0,
#   "average": 210.0,
#   "median": 212.0,
#   "current": 195.0,
#   "num_price_targets": 37,
# }

aapl.forecasts.recommendations()
# DataFrame indexed by date with columns: strongBuy, buy, hold, sell, strongSell
```

!!! note
    `recommendations()` returns ~1 year of history without a Pro account and the full multi-year history with authentication. All other forecast methods return complete data without authentication.

---

## `stock.history`

| Method | Description | Returns |
|---|---|---|
| `prices()` | Daily OHLCV price history | `DataFrame` |
| `market_cap(frequency="annual")` | Historical market cap | `DataFrame` |

`frequency` accepts `"daily"`, `"weekly"`, `"monthly"`, `"quarterly"`, or `"annual"`.

```python
aapl.history.prices()
# DataFrame indexed by date:
#             open    high     low   close      volume  change
# date
# 2020-01-02  296.24  300.60  295.19  300.35  33870100    0.012

aapl.history.market_cap()
aapl.history.market_cap(frequency="monthly")
aapl.history.market_cap(frequency="daily")
```

---

## `stock.company`

| Method | Description | Returns |
|---|---|---|
| `profile()` | Name, sector, industry, country, CEO, IPO date, founded year, employees | `dict` |
| `description()` | Long-form business description | `str` |
| `executives()` | Key executives — name and title | `DataFrame` |

```python
aapl.company.profile()
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

aapl.company.description()
# "Apple Inc. designs, manufactures, and markets smartphones, personal computers..."

aapl.company.executives()
# DataFrame with columns: name, title
#            name               title
# 0      Tim Cook                 CEO
# 1   Luca Maestri                CFO
# ...
```

---

## `stock.dividend`

| Method | Description | Returns |
|---|---|---|
| `info()` | Annual amount, yield, frequency, ex-date, pay-date, payout ratio | `dict` |
| `history()` | Full payment history indexed by ex-dividend date | `DataFrame` |

```python
aapl.dividend.info()
# {
#   "annual_amount": 1.0,
#   "yield_pct": 0.51,
#   "frequency": "Quarterly",
#   "ex_date": "2025-02-07",
#   "pay_date": "2025-02-13",
#   "payout_ratio": 15.2,
#   "summary": "Apple pays a quarterly dividend of $0.25 per share.",
# }

aapl.dividend.history()
# DataFrame indexed by ex_date with columns:
# amount, type, declaration_date, record_date, payment_date
```

---

## `stock.employees`

| Method | Description | Returns |
|---|---|---|
| `history()` | Annual employee headcount over time | `DataFrame` |

```python
aapl.employees.history()
# DataFrame indexed by date with columns: count, change, growth
#             count  change  growth
# date
# 2015-09-26  110000     ...     ...
# 2016-09-24  116000    6000    0.055
```

---

## `stock.metrics`

Segment-level breakdowns. `period` accepts `"quarterly"` (default), `"trailing"`, or `"annual"` (alias for `"trailing"`).

| Method | Description | Returns |
|---|---|---|
| `revenue_by_segment(period="quarterly")` | Revenue by product/service segment | `DataFrame` |
| `gross_profit_by_type(period="quarterly")` | Gross profit by segment type | `DataFrame` |
| `gross_margin_by_type(period="quarterly")` | Gross margin (%) by segment type | `DataFrame` |
| `revenue_by_geography(period="quarterly")` | Revenue by geography | `DataFrame` |
| `operating_expense_breakdown(period="quarterly")` | Operating expenses by category | `DataFrame` |
| `operating_metrics()` | Company-specific operating KPIs (e.g. active devices, subscribers) | `DataFrame` |

```python
aapl.metrics.revenue_by_segment()
# DataFrame with segment names as columns indexed by period
# Example columns for AAPL: iPhone, Mac, iPad, Wearables, Services

aapl.metrics.revenue_by_geography(period="trailing")
aapl.metrics.gross_margin_by_type()
aapl.metrics.operating_expense_breakdown()
aapl.metrics.operating_metrics()
# DataFrame with company-specific metrics, e.g.:
# active_devices, app_store_transactions, apple_tv_subscribers...
```

!!! note
    Not all metrics are available for every ticker. Availability depends on what stockanalysis.com reports for that company.

---

## Direct methods on `Stock`

| Method | Description | Returns |
|---|---|---|
| `overview()` | Price, market cap, P/E, analyst rating, earnings date from the main page | `dict` |
| `ratios(period="annual")` | P/E, P/S, EV/EBITDA, margins, and more | `DataFrame` |
| `statistics()` | All valuation stats as a flat table — section, id, title, value | `DataFrame` |
| `transcripts()` | Earnings call transcript list — date, quarter, summary, audio URL | `DataFrame` |
| `transcript(id)` | Full transcript with AI summary and speaker turns | `dict` |

### `overview()`

```python
aapl.overview()
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
#   "earningsDate": "May 1, 2025",
#   "description": "Apple Inc. designs...",
# }
```

### `ratios()`

```python
aapl.ratios()
aapl.ratios(period="quarterly")
# DataFrame with financial ratios over time, including:
# P/E ratio, P/S ratio, P/B ratio, EV/EBITDA, EV/Sales,
# gross margin, operating margin, net margin, ROE, ROA…
```

### `statistics()`

Returns all valuation statistics as a flat `DataFrame` with columns: `section`, `id`, `title`, `value`.

The 18 available sections are:

| Section | Contents |
|---|---|
| `valuation` | Market cap, enterprise value, P/E, P/S, P/B, P/FCF |
| `shares` | Shares outstanding, float, insider/institutional ownership |
| `ratios` | ROE, ROA, ROIC, debt/equity, current ratio |
| `evRatios` | EV/EBITDA, EV/Sales, EV/FCF, EV/EBIT |
| `financialPosition` | Cash, debt, net cash, working capital |
| `financialEfficiency` | Asset turnover, inventory turnover, receivables turnover |
| `taxes` | Tax rate, deferred tax |
| `stockPrice` | 52-week high/low, 50/200-day moving average, RSI |
| `shortSelling` | Short interest, short ratio, short % of float |
| `incomeStatement` | Revenue, EBITDA, net income, EPS (TTM) |
| `balanceSheet` | Total assets, total liabilities, book value per share |
| `cashFlow` | Operating, investing, financing cash flows, free cash flow |
| `margins` | Gross, operating, net, EBITDA, FCF margins |
| `dividends` | Dividend yield, payout ratio, 5-year growth rate |
| `analystForecasts` | Analyst consensus, price target, EPS estimates |
| `stockSplits` | Split history |
| `scores` | Quality scores, Altman Z-Score, Piotroski F-Score |
| `fairValue` | Estimated intrinsic value |

```python
aapl.statistics()
#         section          id                  title    value
# 0    valuation  marketCap          Market Cap  3.00T
# 1    valuation         pe            P/E Ratio  32.10
# ...
```

### `transcripts()`

```python
transcripts = aapl.transcripts()
# DataFrame with columns: id, date, quarter, fiscal_year, title, summary, audio_url
#     id        date quarter  fiscal_year                     title  ...
# 0  123  2026-05-01      Q2         2026  Apple Q2 2026 Earnings Call ...
```

### `transcript(id)`

```python
transcript_id = transcripts.iloc[0]["id"]
aapl.transcript(transcript_id)
# {
#   "title": "Apple Q2 2026 Earnings Call",
#   "summary_html": "<p>AI-generated summary of the call...</p>",
#   "turns": [
#     {"speaker": "Tim Cook",     "role": "CEO",      "text": "Good afternoon..."},
#     {"speaker": "Luca Maestri", "role": "CFO",      "text": "Thank you Tim..."},
#     {"speaker": "John Analyst", "role": "Analyst",  "text": "Can you comment..."},
#   ],
# }
```

You can pass either the integer `id` from the transcripts DataFrame or the string equivalent.
