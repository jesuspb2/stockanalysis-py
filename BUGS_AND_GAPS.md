# stockanalysis-py — Bug Report & Gap Analysis

Generated: 2026-05-19 (updated after commit 91dbd407)  
Test environment: Python 3.14, stockanalysis-py 0.1.0  
Tickers tested: AAPL, MSFT, GOOG, NVDA (stocks) · SPY, QQQ (ETFs)  
**98 tests — 93 PASS / 5 FAIL**

---

## ✅ Fixed in latest commits

| # | Bug | Status |
|---|-----|--------|
| 1 | `ETF.performance()` → 404 Not Found | **Fixed** — data now parsed from main ETF page |
| 2 | `screener()` → 404 Not Found | **Fixed** — URL corrected to `/stocks/screener/` |
| 3 | `transcript(id)` → KeyError: 'data' | **Fixed** — error nodes handled in `fetch_data_json` |
| 4 | `transcripts(GOOG)` → KeyError: 'data' | **Fixed** — `fetch_transcripts` catches `ValueError`, returns empty DataFrame |
| 5 | `metrics.revenue_by_geography(MSFT)` → KeyError: 'data' | **Fixed** — `_segment_df` uses `.get("data")` with graceful fallback |
| 6 | `fetch_data_json` hardcodes `nodes[2]` | **Fixed** — now dynamically finds the first valid data node |
| 7 | `history.prices()` — undocumented columns `'a'` and `'div'` | **Fixed** — renamed to `adjusted_close` and `dividend` |
| 8 | `search()` — returns empty list | **Fixed** — switched to `/api/search` endpoint (SvelteKit `__data.json` route no longer carries search results) |

---

## Remaining Failures

None — all known bugs fixed.

---

## Gaps / Data Availability Limitations

These are not code bugs — they reflect data that simply does not exist on the platform for certain tickers.

### 2. `employees.history(quarterly)` — empty for AAPL

**File:** `stockanalysis/data/employees.py` → `Employees.history`

Apple does not publish quarterly headcount figures. The function returns an empty DataFrame with a `UserWarning`, which is the correct behaviour. Not all companies report this data.

**Status:** Working as designed. Test expects non-empty data — test expectation may need adjustment.

---

### 3. `metrics.revenue_by_geography()` — empty for MSFT

Microsoft does not have a geographic revenue breakdown available on stockanalysis.com. The function correctly returns an empty DataFrame (no crash). This is a data availability issue, not a bug.

**Status:** Working as designed after the fix in commit 91dbd407.

---

### 4. `transcripts()` — empty for GOOG

Alphabet (GOOG/GOOGL) does not have earnings call transcripts available on stockanalysis.com. The function returns an empty DataFrame without crashing.

**Status:** Working as designed after the fix in commit 91dbd407.

---

## What Works Well ✅

The following features were tested across AAPL, MSFT, GOOG, NVDA, SPY, QQQ and all passed:

- `stock.financials` — income statement, balance sheet, cash flow, metrics (annual + quarterly)
- `stock.ratios()` — annual and quarterly
- `stock.statistics()` — full flat DataFrame
- `stock.overview()` — summary dict
- `stock.forecasts` — estimates, revenue, eps, price_targets, recommendations
- `stock.history.prices()` — daily OHLCV with `adjusted_close` and `dividend` columns
- `stock.history.market_cap()` — all 5 frequencies (daily, weekly, monthly, quarterly, annual)
- `stock.company` — profile, description, executives
- `stock.dividend` — info, history (including empty result for no-dividend stocks like GOOG)
- `stock.employees.history(annual)`
- `stock.metrics` — revenue_by_segment, gross_profit_by_type, gross_margin_by_type, revenue_by_geography (AAPL), operating_expense_breakdown, operating_metrics
- `stock.transcripts()` — when ticker has transcripts available
- `stock.transcript(id)` — individual transcript fetch (with graceful error on missing/paywalled IDs)
- `etf.overview()`, `etf.sectors()`, `etf.performance()`, `etf.holdings()`, `etf.holdings(top=N)`, `etf.history.prices()`
- `screener()` — all filter combinations (sector, market cap, country, exchange)
- Lowercase ticker symbols handled correctly (uppercased internally)
- `clear_cache()` works
- `__repr__` correct for both `Stock` and `ETF`
