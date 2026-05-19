# stockanalysis-py — Bug Report & Gap Analysis

Generated: 2026-05-19  
Test environment: Python 3.14, stockanalysis-py 0.1.0  
Tickers tested: AAPL, MSFT, GOOG, NVDA (stocks) · SPY, QQQ (ETFs)  
**98 tests — 87 PASS / 11 FAIL**

---

## Critical Bugs

### 1. `ETF.performance()` → 404 Not Found

**File:** `stockanalysis/data/etf_overview.py` → `fetch_etf_performance`

The function fetches `/etf/{symbol}/performance/__data.json`, which does not exist on the site.

Performance data is already present on the main ETF page (`/etf/{symbol}/__data.json`) under the `performance` key, with fields: `tr1m`, `trYTD`, `tr1y`, `cagr5y`, `cagr10y`, `cagrMAX`.

**Fix:** Change `fetch_etf_performance` to reuse the data from the main ETF page instead of hitting a separate `/performance` route. Example response shape:

```json
{
  "tr1m": 4.015,
  "trYTD": 8.619,
  "tr1y": 25.736,
  "cagr5y": 13.745,
  "cagr10y": 15.563,
  "cagrMAX": 10.815
}
```

The DataFrame columns should be renamed to human-readable names (`1m`, `YTD`, `1y`, `5y_cagr`, `10y_cagr`, `max_cagr` or similar).

---

### 2. `screener()` → 404 Not Found

**File:** `stockanalysis/data/search.py` → `screener`

Wrong URL: the function calls `/screener/stock/__data.json`, which returns 404.

**Correct URL:** `/stocks/screener/__data.json`

Additionally, the response node structure is different from most endpoints — data is in `nodes[1]`, not `nodes[2]`. The `fetch_data_json` helper cannot be used directly here; the screener needs its own node-resolution logic (same pattern as `search()`).

```python
# Current (broken)
url = f"{BASE}/screener/stock/__data.json"

# Should be
url = f"{BASE}/stocks/screener/__data.json"
# And read from nodes[1], not nodes[2]
```

---

### 3. `search()` → IndexError: list index out of range

**File:** `stockanalysis/data/search.py` → `search`

The function reads `payload["nodes"][2]["data"]`, but the search endpoint only returns 2 nodes (`nodes[0]` and `nodes[1]`). `nodes[2]` does not exist.

The actual search results are not in `nodes[0]` either — `nodes[0]` only contains session/auth data. The search endpoint appears to have changed on the site; `nodes[1]` now returns a 404 error. The search feature is **fully broken** and needs the correct endpoint URL to be rediscovered.

---

### 4. `transcript(id)` → KeyError: 'data'

**File:** `stockanalysis/core/http.py` → `fetch_data_json`

`fetch_data_json` accesses `resp.json()["nodes"][2]["data"]` unconditionally. When an endpoint returns an error (e.g. transcript not found, or requires authentication), `nodes[2]` has this structure:

```json
{ "type": "error", "error": { "message": "not found" }, "status": 404 }
```

There is no `"data"` key, so a `KeyError` is raised instead of a meaningful exception.

**Fix:** Before accessing `["data"]`, check that the target node has `"type": "data"` and not `"type": "error"`. Raise a descriptive exception when an error node is encountered:

```python
node = resp.json()["nodes"][2]
if node.get("type") == "error":
    raise ValueError(f"API error {node.get('status')}: {node['error'].get('message')}")
data = node["data"]
```

---

### 5. `transcripts(GOOG)` → KeyError: 'data'

**File:** `stockanalysis/data/transcripts.py` → `fetch_transcripts`  
**Root cause:** same as Bug #4

GOOG does not have earnings call transcripts on stockanalysis.com (GOOGL does). The endpoint returns an error node at `nodes[2]`, which crashes `fetch_data_json`.

**Fix:** Once Bug #4 is fixed, this will either raise a clean error or should return an empty DataFrame with a warning. Consider catching the error and returning `pd.DataFrame()` when the transcript list is unavailable.

---

### 6. `metrics.revenue_by_geography(MSFT)` → KeyError: 'data'

**File:** `stockanalysis/data/metrics.py` → `_segment_df`

```python
def _segment_df(node_data, period):
    meta = node_data[0]
    data_top = resolve(meta["data"], node_data)  # KeyError if "data" not in meta
```

Not all segment metrics endpoints include a `"data"` key in `meta`. This fails for MSFT's `revenue_by_geography` and likely other tickers/metrics combinations.

**Fix:** Use `.get()` and handle the missing key gracefully:

```python
data_ref = meta.get("data")
if data_ref is None:
    return pd.DataFrame()
data_top = resolve(data_ref, node_data)
```

---

## Gaps / Missing Features

### 7. `history.prices()` — undocumented columns `'a'` and `'div'`

**File:** `stockanalysis/data/history.py` → `History.prices`  
Same issue in `stockanalysis/data/etf_history.py` → `ETFHistory.prices`

The API returns two columns that are not in the rename map:

| API key | Meaning | Should be renamed to |
|---------|---------|----------------------|
| `a`     | Adjusted close price | `adjusted_close` |
| `div`   | Dividend paid on that date | `dividend` |

**Actual columns returned:** `['a', 'close', 'high', 'low', 'open', 'volume', 'change', 'div']`  
**Documented columns:** `open, high, low, close, volume, change`

**Fix:** Add these two entries to the rename dict:

```python
df = df.rename(columns={
    "t": "date",
    "o": "open",
    "h": "high",
    "l": "low",
    "c": "close",
    "v": "volume",
    "ch": "change",
    "a": "adjusted_close",   # add this
    "div": "dividend",        # add this
})
```

---

### 8. `employees.history(quarterly)` — returns empty DataFrame silently

**File:** `stockanalysis/data/employees.py` → `Employees.history`

For many companies (confirmed: AAPL), quarterly employee data is not published. The function returns an empty DataFrame with no warning, making it hard to distinguish "no data" from a bug.

**Fix:** Log a warning or add a note in the docstring that quarterly data may not be available for all companies.

---

### 9. `fetch_data_json` hardcodes `nodes[2]` — fragile

**File:** `stockanalysis/core/http.py` → `fetch_data_json`

The function always reads `resp.json()["nodes"][2]["data"]`. The actual index of the data node varies by endpoint:

| Endpoint | Data node index |
|----------|----------------|
| Most stock/ETF pages | `nodes[2]` |
| Screener | `nodes[1]` |
| Search | not at `nodes[2]` (endpoint broken) |
| Transcript (error) | `nodes[2]` has type `"error"` |

**Fix:** Dynamically find the data node instead of hardcoding index 2:

```python
nodes = resp.json()["nodes"]
data_node = next(
    (n for n in reversed(nodes) if n.get("type") == "data" and "data" in n),
    None,
)
if data_node is None:
    error_node = next((n for n in nodes if n.get("type") == "error"), None)
    msg = error_node["error"].get("message", "unknown") if error_node else "no data node"
    raise ValueError(f"API returned no data: {msg}")
data = data_node["data"]
```

---

## What Works Well ✅

The following features were tested across AAPL, MSFT, GOOG, NVDA, SPY, QQQ and all passed:

- `stock.financials` — income statement, balance sheet, cash flow, metrics (annual + quarterly)
- `stock.ratios()` — annual and quarterly
- `stock.statistics()` — full flat DataFrame
- `stock.overview()` — summary dict
- `stock.forecasts` — estimates, revenue, eps, price_targets, recommendations
- `stock.history.prices()` — daily OHLCV (plus undocumented `a`, `div` columns, see Gap #7)
- `stock.history.market_cap()` — all 5 frequencies (daily, weekly, monthly, quarterly, annual)
- `stock.company` — profile, description, executives
- `stock.dividend` — info, history (including empty result for no-dividend stocks like GOOG)
- `stock.employees.history(annual)`
- `stock.metrics` — revenue_by_segment, gross_profit_by_type, gross_margin_by_type, operating_expense_breakdown, operating_metrics (AAPL, NVDA)
- `stock.transcripts()` — when ticker has transcripts and endpoint doesn't error
- `etf.overview()`, `etf.sectors()`, `etf.holdings()`, `etf.holdings(top=N)`, `etf.history.prices()`
- Lowercase ticker symbols handled correctly (uppercased internally)
- `clear_cache()` works
- `__repr__` correct for both `Stock` and `ETF`
