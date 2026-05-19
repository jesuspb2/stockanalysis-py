# API Reference

Auto-generated from source docstrings.

---

## Top-level functions

::: stockanalysis
    options:
      members:
        - stock
        - etf
        - search
        - screener
        - clear_cache
      show_root_heading: false

---

## Stock

::: stockanalysis.stock.Stock
    options:
      members:
        - overview
        - ratios
        - statistics
        - transcripts
        - transcript

---

## Stock namespaces

### Financials

::: stockanalysis.data.financials.Financials
    options:
      members:
        - income_statement
        - balance_sheet
        - cash_flow
        - kpis

### Forecasts

::: stockanalysis.data.forecast.Forecasts
    options:
      members:
        - estimates
        - revenue
        - eps
        - price_targets
        - recommendations

### History

::: stockanalysis.data.history.History
    options:
      members:
        - prices
        - market_cap

### Company

::: stockanalysis.data.company.Company
    options:
      members:
        - profile
        - description
        - executives

### Dividend

::: stockanalysis.data.dividend.Dividend
    options:
      members:
        - info
        - history

### Employees

::: stockanalysis.data.employees.Employees
    options:
      members:
        - history

### Metrics

::: stockanalysis.data.metrics.Metrics
    options:
      members:
        - revenue_by_segment
        - gross_profit_by_type
        - gross_margin_by_type
        - revenue_by_geography
        - operating_expense_breakdown
        - operating_metrics

### Statistics

::: stockanalysis.data.statistics.Statistics
    options:
      members:
        - all
        - to_dataframe

---

## ETF

::: stockanalysis.etf.ETF
    options:
      members:
        - overview
        - sectors
        - performance

### ETFHoldings

::: stockanalysis.data.etf_holdings.ETFHoldings

### ETFHistory

::: stockanalysis.data.etf_history.ETFHistory
