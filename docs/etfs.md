# ETFs

Create an `ETF` object with `sa.etf("TICKER")` and access data through its methods and namespaces.

```python
import stockanalysis as sa

spy = sa.etf("SPY")
```

The ticker is case-insensitive — `sa.etf("spy")` and `sa.etf("SPY")` are equivalent.

---

## Methods

| Method | Description | Returns |
|---|---|---|
| `overview()` | AUM, expense ratio, NAV, inception date, category, issuer, and more | `dict` |
| `holdings(top=None)` | Full holdings list; pass `top=N` to limit to N largest positions | `DataFrame` |
| `sectors()` | Sector allocation with weights | `DataFrame` |
| `performance()` | Returns by period: 1m, YTD, 1y, 3y CAGR, 5y CAGR, 10y CAGR, max CAGR | `DataFrame` |
| `history.prices()` | Daily OHLCV price history | `DataFrame` |

---

## Examples

### `overview()`

Returns a `dict` with the following keys:

| Key | Description |
|---|---|
| `description` | Fund description |
| `expenseRatio` | Annual expense ratio (e.g. `0.0945` for 0.0945%) |
| `aum` | Assets under management in USD |
| `nav` | Net asset value per share |
| `inceptionDate` | Fund launch date |
| `index` | Tracked index (e.g. `"S&P 500"`) |
| `category` | Morningstar category (e.g. `"Large Blend"`) |
| `issuer` | Fund issuer (e.g. `"State Street"`) |
| `assetClass` | Asset class (e.g. `"Equity"`, `"Fixed Income"`) |
| `numHoldings` | Number of holdings |
| `dividend` | Most recent dividend amount |
| `dividendYield` | Annual dividend yield |
| `pe` | Price-to-earnings ratio |
| `beta` | Beta vs. the market |

```python
spy.overview()
# {
#   "description": "SPDR S&P 500 ETF Trust tracks the S&P 500 index...",
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
```

### `holdings(top=None)`

Returns all holdings by default. Pass `top=N` to get only the N largest by weight.

```python
spy.holdings()       # all 503 holdings
spy.holdings(top=10) # top 10 by weight

# DataFrame with columns: rank, name, symbol, weight_pct, shares
#    rank               name  symbol  weight_pct        shares
# 0     1       Apple Inc.    AAPL        7.12  5_200_000_000
# 1     2    Microsoft Corp    MSFT        6.89  4_100_000_000
# ...
```

### `sectors()`

```python
spy.sectors()
# DataFrame with columns: sector, weight
#                     sector  weight
# 0         Information Tech    31.2
# 1              Financials    13.1
# 2            Health Care    12.8
# ...
```

### `performance()`

Returns by time period. Periods longer than 1 year are reported as compound annual growth rates (CAGR).

```python
spy.performance()
# DataFrame with columns: period, return
#       period   return
# 0         1m     2.15
# 1        YTD    10.45
# 2         1y    18.32
# 3     3y_cagr   12.10
# 4     5y_cagr   14.50
# 5    10y_cagr   13.80
# 6    max_cagr   10.90
```

### `history.prices()`

```python
spy.history.prices()
# DataFrame indexed by date with columns: open, high, low, close, volume, change
#             open    high     low   close     volume  change
# date
# 1993-01-29  43.97   44.25   43.97   43.94  1003200    -0.001
# ...
```
