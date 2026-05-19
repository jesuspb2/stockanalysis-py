# Installation

## Requirements

- Python 3.10+
- `pandas` ≥ 2.0
- `httpx` ≥ 0.27

## Install

```bash
pip install git+https://github.com/jesuspb2/stockanalysis-py.git
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add git+https://github.com/jesuspb2/stockanalysis-py.git
```

## Verify

```python
import stockanalysis as sa

aapl = sa.stock("AAPL")
print(aapl.overview())
```

---

## Pro authentication (optional)

Authentication is required to unlock extended historical data for certain endpoints:

- `forecasts.recommendations()` — returns ~1 year of history without auth and the full multi-year history with auth.
- All other endpoints return complete data without authentication.

### Setup

**1. Install with the `auth` extra** to pull in Playwright:

```bash
pip install "stockanalysis-py[auth] @ git+https://github.com/jesuspb2/stockanalysis-py.git"
```

Or with uv:

```bash
uv add "stockanalysis-py[auth] @ git+https://github.com/jesuspb2/stockanalysis-py.git"
```

**2. Install the Chromium browser binary** (only needed once after first install):

```bash
playwright install chromium
```

**3. Add your credentials** to a `.env` file at the project root:

```bash
SA_EMAIL=you@example.com
SA_PASSWORD=yourpassword
```

**4. Run the one-time login command:**

```bash
stockanalysis-login
```

This launches a headless browser, logs in to stockanalysis.com, and saves the session cookies to `.auth/state.json`. All subsequent library calls will load that file automatically.

### Re-authentication

You only need to re-run `stockanalysis-login` if the session expires. The session path can be customized with the `SA_STATE_PATH` environment variable:

```bash
SA_STATE_PATH=/custom/path/state.json stockanalysis-login
```

!!! note
    The `.auth/` directory contains your session cookies. Add it to `.gitignore` to avoid committing credentials.

```gitignore
.auth/
.env
```
