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
| `country` | `str` | Country name as shown on stockanalysis.com (e.g. `"United States"`, `"China"`, `"United Kingdom"`) |
| `exchange` | `str` | Exchange name (e.g. `"NYSE"`, `"NASDAQ"`, `"NYSEAMERICAN"`) |
| `filters` | `dict` | Numeric range filters — see [Filters](#filters) below |
| `**extra_params` | `str` | Additional raw parameters forwarded to the screener endpoint |

### Return value

Returns a `DataFrame` with one row per stock and the following columns:

| Column | Description |
|---|---|
| `symbol` | Ticker symbol |
| `name` | Company name |
| `marketCap` | Market capitalization in USD |
| `price` | Current stock price |
| `change` | Price change 1D (%) |
| `industry` | Industry classification |
| `volume` | Trading volume |
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

### Filters

The `filters` parameter accepts a dict of `{key: (min, max)}` tuples. Use `None` for an unbounded side.

| Key | Description |
|---|---|
| **Price & Volume** | |
| `price` | Stock price |
| `volume` | Trading volume |
| `change` | Price change 1D (%) |
| `avg_volume` | Average trading volume |
| `beta` | Beta (5Y) |
| `rsi` | RSI (14-day) |
| **Valuation** | |
| `pe_ratio` | P/E ratio (TTM) |
| `pe_forward` | Forward P/E |
| `pb_ratio` | P/B ratio |
| `ps_ratio` | P/S ratio |
| `peg_ratio` | PEG ratio |
| `ev_ebitda` | EV/EBITDA |
| `dividend_yield` | Dividend yield (%) |
| **Growth** | |
| `revenue_growth` | Revenue growth YoY (%) |
| `eps_growth` | EPS growth YoY (%) |
| `price_change_1y` | Price change over the last 12 months (%) |
| **Profitability** | |
| `gross_margin` | Gross margin (%) |
| `operating_margin` | Operating margin (%) |
| `net_margin` | Net profit margin (%) |
| `roe` | Return on equity (%) |
| `roic` | Return on invested capital (%) |
| **Financial Strength** | |
| `debt_equity` | Debt-to-equity ratio |
| `current_ratio` | Current ratio |

Passing an unknown key raises a `ValueError` listing all valid keys.

### Examples

```python
import stockanalysis as sa

# Large-cap technology companies
sa.screener(sector="Technology", market_cap_min=10e9)

# Filter by country and exchange
sa.screener(country="China", market_cap_min=5e9)
sa.screener(exchange="NYSE", market_cap_min=50e9)

# Valuation: cheap large-caps with growth
sa.screener(
    market_cap_min=10e9,
    filters={
        "pe_ratio": (None, 15),
        "ps_ratio": (None, 2),
        "revenue_growth": (5, None),
    },
)

# Quality: profitable companies with strong returns and low debt
sa.screener(
    market_cap_min=5e9,
    filters={
        "roe": (15, None),
        "roic": (10, None),
        "gross_margin": (40, None),
        "debt_equity": (None, 1),
    },
)

# Dividend: high yield, sustainable payout
sa.screener(
    market_cap_min=2e9,
    filters={
        "dividend_yield": (3, 10),   # between 3% and 10% (avoids yield traps)
        "debt_equity": (None, 2),
        "current_ratio": (1, None),
    },
)

# Growth: high revenue and EPS growth, not overpriced
sa.screener(
    sector="Technology",
    filters={
        "revenue_growth": (20, None),
        "eps_growth": (15, None),
        "pe_forward": (None, 40),
    },
)

# Technical: oversold large-caps
sa.screener(
    market_cap_min=10e9,
    filters={
        "rsi": (None, 35),
        "price_change_1y": (None, -10),  # down >10% in the last year
    },
)

# Combined: US tech mega-caps with strong fundamentals
sa.screener(
    sector="Technology",
    country="United States",
    market_cap_min=50e9,
    filters={
        "gross_margin": (50, None),
        "operating_margin": (20, None),
        "revenue_growth": (8, None),
        "pe_forward": (None, 35),
    },
)
```

---

## Cache

HTTP responses are cached in-session to avoid duplicate requests. Call `clear_cache()` to reset between runs in a long-lived process (e.g. a Jupyter notebook session).

```python
sa.clear_cache()
```
