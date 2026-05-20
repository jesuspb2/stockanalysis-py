# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed

- `sa.screener()`: `country` and `exchange` parameters now work correctly — they post-filter results via the `/_api/endpoints/screener/data-point` endpoint (previously declared but silently ignored).
  - `country` accepts full country names (e.g. `"United States"`, `"China"`).
  - `exchange` accepts exchange codes (e.g. `"NYSE"`, `"NASDAQ"`, `"NYSEAMERICAN"`).

### Added

- `sa.screener()`: new `filters` parameter — a dict of `{key: (min, max)}` tuples for numeric range filtering. Supports 23 keys across valuation, growth, profitability, financial strength, and technicals:
  - **Price & Volume**: `price`, `volume`, `change`, `avg_volume`, `beta`, `rsi`
  - **Valuation**: `pe_ratio`, `pe_forward`, `pb_ratio`, `ps_ratio`, `peg_ratio`, `ev_ebitda`, `dividend_yield`
  - **Growth**: `revenue_growth`, `eps_growth`, `price_change_1y`
  - **Profitability**: `gross_margin`, `operating_margin`, `net_margin`, `roe`, `roic`
  - **Financial Strength**: `debt_equity`, `current_ratio`

## [0.1.0] - 2026-05-18

### Added

- `Stock` class with the following namespaces:
  - `Financials` — income statement, balance sheet, and cash flow data
  - `Forecasts` — analyst price targets and earnings estimates
  - `Statistics` — key financial statistics and ratios
  - `Company` — company profile and general information
  - `History` — historical price data
  - `Dividend` — dividend history and yield data
  - `Employees` — employee count history
  - `Metrics` — financial metrics and performance indicators
- `ETF` class with the following namespaces:
  - `Holdings` — top holdings and weights
  - `History` — historical price data
  - `Overview` — fund overview and metadata
  - `Sectors` — sector allocation breakdown
  - `Performance` — fund performance across time periods
- `sa.search()` — search for stocks and ETFs by name or ticker
- `sa.screener()` — screen stocks based on financial filters
- `sa.clear_cache()` — clear the local HTTP response cache
- HTTP response cache to reduce redundant network requests
- Thread-safe session singleton for efficient connection reuse
- Pro account authentication via CLI (`stockanalysis-login` command)
