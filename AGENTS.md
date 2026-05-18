# stockanalysis-py — Agent Instructions

Python library for extracting data from [stockanalysis.com](https://stockanalysis.com).
Installable via `uv add stockanalysis-py` or `pip install stockanalysis-py`.

---

## Project goal

A typed Python library with a clean OOP API, similar to yfinance but for stockanalysis.com.
Scrapes data using the site's internal SvelteKit `__data.json` endpoints (no browser needed for most calls).
Pro account cookies are loaded automatically from `.auth/state.json`.

---

## Architecture

```
src/stockanalysis/
├── __init__.py            # sa.stock("AAPL") entry point
├── stock.py               # Stock class — public API surface
├── auth.py                # CLI: stockanalysis-login (saves session to .auth/state.json)
├── core/
│   ├── __init__.py        # re-exports get_session, fetch_data_json, resolve, extract_*
│   ├── session.py         # httpx.Client singleton — loads cookies from .auth/state.json
│   └── http.py            # fetch_data_json(), resolve(), extract_financial_df(), extract_metrics_df()
└── data/
    ├── __init__.py        # re-exports all namespace classes and fetch_* functions
    ├── financials.py      # Financials class
    ├── forecast.py        # Forecasts class
    ├── statistics.py      # Statistics class
    ├── company.py         # Company class
    ├── history.py         # History class
    ├── dividend.py        # Dividend class
    ├── employees.py       # Employees class
    ├── metrics.py         # Metrics class (segment breakdowns)
    ├── overview.py        # fetch_overview()
    └── transcripts.py     # fetch_transcripts()
```

### Key conventions

- **SvelteKit dedup encoding**: all `__data.json` responses store values once in a flat array and reference them by index. Use `resolve(val, node_data)` from `core/http.py` to decode.
- **`node_data`**: always `response["nodes"][2]["data"]`. `node_data[0]` is the meta dict with index pointers to all data sections.
- **Session**: `get_session()` from `core/session.py` returns a singleton `httpx.Client`. If `.auth/state.json` exists, cookies are loaded automatically. Never pass sessions around manually.
- **Namespace classes** (`Financials`, `Forecasts`, etc.) are instantiated once in `Stock.__init__` and stored as attributes. They only hold `self._symbol`.
- **`core/`** is infrastructure (HTTP, session). **`data/`** is all domain modules. Only `stock.py`, `auth.py`, and `__init__.py` are public.
- **`resolve_meta(node_data)`**: convenience helper in `core/http.py` that resolves every key in `node_data[0]` at once — useful when inspecting a new endpoint.

---

## Public API

```python
import stockanalysis as sa

stock = sa.stock("AAPL")

# Financials (annual or quarterly)
stock.financials.income_statement(period="annual")
stock.financials.balance_sheet(period="quarterly")
stock.financials.cash_flow()
stock.ratios(period="annual")

# Analyst forecasts
stock.forecasts.estimates(period="annual")   # full estimates table → DataFrame
stock.forecasts.revenue(period="annual")     # → Series
stock.forecasts.eps(period="annual")         # → Series
stock.forecasts.price_targets()              # → dict
stock.forecasts.recommendations()            # → DataFrame

# Valuation & stats
stock.statistics()                           # all sections → flat DataFrame

# Company info
stock.company.profile()                      # → dict
stock.company.description()                  # → str
stock.company.executives()                   # → DataFrame

# Price & market cap history
stock.history.prices()                       # daily OHLCV → DataFrame
stock.history.market_cap(frequency="annual") # → DataFrame

# Dividend
stock.dividend.info()                        # → str summary
stock.dividend.history()                     # → DataFrame

# Employees
stock.employees.history(period="annual")     # → DataFrame

# Segment breakdowns & operating metrics
stock.metrics.revenue_by_segment()
stock.metrics.gross_profit_by_type()
stock.metrics.gross_margin_by_type()
stock.metrics.revenue_by_geography()
stock.metrics.operating_expense_breakdown()
stock.metrics.operating_metrics()            # annual device/user counts → DataFrame
```

---

## Authentication (Pro)

Credentials go in `.env` at the repo root (gitignored):

```
SA_EMAIL=you@example.com
SA_PASSWORD=yourpassword
```

Run once to save the session:

```bash
uv run stockanalysis-login
```

State is saved to `.auth/state.json` (gitignored). The session is picked up automatically on the next import — no code change needed.

---

## Development

```bash
uv run pytest tests/ -v          # run all tests
uv run stockanalysis-login       # refresh session
uv run python -c "import stockanalysis as sa; print(sa.stock('AAPL').company.profile())"
```

Tests live in `tests/`. Each namespace class has its own test file or group in `test_stock.py`.
Tests hit the real network — no mocking. Run them to verify a new endpoint works before committing.

---

## Implemented endpoints

| Method | URL | Status |
|---|---|---|
| `financials.income_statement()` | `/stocks/{symbol}/financials/` | ✅ |
| `financials.balance_sheet()` | `/stocks/{symbol}/financials/balance-sheet/` | ✅ |
| `financials.cash_flow()` | `/stocks/{symbol}/financials/cash-flow-statement/` | ✅ |
| `ratios()` | `/stocks/{symbol}/financials/ratios/` | ✅ |
| `forecasts.estimates()` | `/stocks/{symbol}/forecast/` | ✅ |
| `forecasts.revenue()` | `/stocks/{symbol}/forecast/` | ✅ |
| `forecasts.eps()` | `/stocks/{symbol}/forecast/` | ✅ |
| `forecasts.price_targets()` | `/stocks/{symbol}/forecast/` | ✅ |
| `forecasts.recommendations()` | `/stocks/{symbol}/forecast/` | ✅ |
| `statistics()` | `/stocks/{symbol}/statistics/` | ✅ |
| `history.prices()` | `/stocks/{symbol}/history/` | ✅ |
| `history.market_cap()` | `/stocks/{symbol}/market-cap/` | ✅ |
| `company.profile()` | `/stocks/{symbol}/company/` | ✅ |
| `company.description()` | `/stocks/{symbol}/company/` | ✅ |
| `company.executives()` | `/stocks/{symbol}/company/` | ✅ |
| `dividend.info()` | `/stocks/{symbol}/dividend/` | ✅ |
| `dividend.history()` | `/stocks/{symbol}/dividend/` | ✅ |
| `employees.history()` | `/stocks/{symbol}/employees/` | ✅ |
| `financials.metrics()` | `/stocks/{symbol}/financials/metrics/` | ✅ |
| `overview()` | `/stocks/{symbol}/` | ✅ |
| `metrics.revenue_by_segment()` | `/stocks/{symbol}/metrics/revenue-by-segment/` | ✅ |
| `metrics.gross_profit_by_type()` | `/stocks/{symbol}/metrics/gross-profit-by-type/` | ✅ |
| `metrics.gross_margin_by_type()` | `/stocks/{symbol}/metrics/gross-margin-by-type/` | ✅ |
| `metrics.revenue_by_geography()` | `/stocks/{symbol}/metrics/revenue-by-geography/` | ✅ |
| `metrics.operating_expense_breakdown()` | `/stocks/{symbol}/metrics/operating-expense-breakdown/` | ✅ |
| `transcripts()` | `/stocks/{symbol}/transcripts/` | ✅ |
| `metrics.operating_metrics()` | `/stocks/{symbol}/metrics/` | ✅ |


---

## Pending endpoints

None — all known endpoints are implemented.

### How to add a new endpoint

1. Fetch `node_data` via `fetch_data_json(path)` from `core/http.py`.
2. Inspect `node_data[0]` to find the relevant key (e.g. `"financialData"`, `"data"`, `"profile"`).
3. Decode with `resolve(meta[key], node_data)`.
4. If it's a financial table → use `extract_financial_df(node_data)`.
5. Add a method to the appropriate class in `data/`, or create a new `data/module.py`.
6. Export it from `data/__init__.py` and wire it up in `Stock.__init__` in `stock.py`.
7. Add a test in `tests/test_stock.py`.

---

## All known URLs (reference)

These are the pages discovered on stockanalysis.com. All follow the pattern
`https://stockanalysis.com/stocks/{symbol}/...` and expose a `__data.json` endpoint.

```
# Main
https://stockanalysis.com/stocks/aapl/

# Financials
https://stockanalysis.com/stocks/aapl/financials/
https://stockanalysis.com/stocks/aapl/financials/balance-sheet/
https://stockanalysis.com/stocks/aapl/financials/cash-flow-statement/
https://stockanalysis.com/stocks/aapl/financials/ratios/
https://stockanalysis.com/stocks/aapl/financials/metrics/

# Forecasts
https://stockanalysis.com/stocks/aapl/forecast/

# Valuation & price
https://stockanalysis.com/stocks/aapl/statistics/
https://stockanalysis.com/stocks/aapl/market-cap/

# Custom metrics (breakdowns)
https://stockanalysis.com/stocks/aapl/metrics/
https://stockanalysis.com/stocks/aapl/metrics/revenue-by-segment/
https://stockanalysis.com/stocks/aapl/metrics/gross-profit-by-type/
https://stockanalysis.com/stocks/aapl/metrics/gross-margin-by-type/
https://stockanalysis.com/stocks/aapl/metrics/revenue-by-geography/
https://stockanalysis.com/stocks/aapl/metrics/operating-expense-breakdown/

# Dividends & price history
https://stockanalysis.com/stocks/aapl/dividend/
https://stockanalysis.com/stocks/aapl/history/

# Company
https://stockanalysis.com/stocks/aapl/company/
https://stockanalysis.com/stocks/aapl/employees/

# Content
https://stockanalysis.com/stocks/aapl/transcripts/
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `httpx` | HTTP — all data fetching |
| `pandas` | DataFrames |
| `python-dotenv` | Load `.env` credentials |
| `playwright` | Login only (`stockanalysis-login` CLI) — optional extra `[auth]` |
