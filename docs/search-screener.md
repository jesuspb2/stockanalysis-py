# Search & Screener

## `sa.search(query)`

Search for stocks, ETFs, and indices by name or ticker symbol.

```python
import stockanalysis as sa

results = sa.search("Apple")
# [
#   {"symbol": "AAPL", "name": "Apple Inc.", "type": "stock"},
#   {"symbol": "AAPL.BA", "name": "Apple Inc.", "type": "stock"},
#   ...
# ]
```

Returns a list of dicts with keys:

| Key | Description |
|---|---|
| `symbol` | Ticker symbol (e.g. `"AAPL"`) |
| `name` | Company or fund name |
| `type` | One of `"stock"`, `"etf"`, or `"index"` |

```python
# Search by ticker
sa.search("MSFT")

# Search by name
sa.search("Berkshire")

# Returns empty list on no results or network error
sa.search("xyzxyznotastock")  # []
```

---

## `sa.screener(...)`

Filter stocks by fundamental criteria. All parameters are optional — omitting all returns the full universe.

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `market_cap_min` | `float` | Minimum market cap in USD (e.g. `10e9` for $10B) |
| `market_cap_max` | `float` | Maximum market cap in USD |
| `sector` | `str` | One of the 11 GICS sectors (see below) |
| `country` | `str` | ISO country code (e.g. `"US"`, `"CN"`, `"GB"`, `"DE"`) |
| `exchange` | `str` | Exchange name (e.g. `"NYSE"`, `"NASDAQ"`) |
| `**extra_params` | `str` | Additional raw filter parameters passed directly to the endpoint |

### Return value

Returns a `DataFrame` with one row per stock and the following columns:

| Column | Description |
|---|---|
| `symbol` | Ticker symbol |
| `name` | Company name |
| `marketCap` | Market capitalization in USD |
| `price` | Current stock price |
| `change` | Price change (%) |
| `industry` | Industry classification |
| `peRatio` | Price-to-earnings ratio |

### Valid sectors

The `sector` parameter must be one of the 11 GICS sectors:

```
"Communication Services"   "Consumer Discretionary"   "Consumer Staples"
"Energy"                   "Financials"                "Healthcare"
"Industrials"              "Materials"                 "Real Estate"
"Technology"               "Utilities"
```

Passing an invalid sector raises a `ValueError`.

### Examples

```python
import stockanalysis as sa

# Large-cap technology companies
sa.screener(sector="Technology", market_cap_min=10e9)

# US healthcare stocks on NYSE
sa.screener(sector="Healthcare", country="US", exchange="NYSE")

# Mid-cap range across all sectors
sa.screener(market_cap_min=2e9, market_cap_max=10e9)

# Small-cap financials in the UK
sa.screener(sector="Financials", country="GB", market_cap_max=2e9)

# Combine with extra endpoint params (advanced)
sa.screener(sector="Technology", country="US", revenue="1000000000-")
```

---

## Cache

HTTP responses are cached in-session to avoid duplicate requests. Call `clear_cache()` to reset between runs in a long-lived process (e.g. a Jupyter notebook session).

```python
sa.clear_cache()
```
