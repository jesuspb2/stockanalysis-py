# Changelog

All notable changes to this project will be documented in this file.

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
