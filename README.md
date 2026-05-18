# stockanalysis-py

Python library for extracting data from [stockanalysis.com](https://stockanalysis.com).

## Installation

```bash
pip install stockanalysis-py
```

## Quick start

```python
import stockanalysis as sa

stock = sa.stock("AAPL")
stock.financials.income_statement()
stock.forecasts.estimates()
stock.company.profile()
stock.history.prices()

etf = sa.etf("SPY")
etf.holdings()
etf.sectors()

sa.search("Apple")
sa.screener(sector="Technology", market_cap_min=10e9)
```

## Authentication (Pro)

```bash
# Add credentials to .env
SA_EMAIL=you@example.com
SA_PASSWORD=yourpassword

# Save session
uv run stockanalysis-login
```

## License

MIT
