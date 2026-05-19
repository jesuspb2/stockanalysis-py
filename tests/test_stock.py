from __future__ import annotations

from typing import Literal

import pandas as pd
import pytest

import stockanalysis as sa

Period = Literal["annual", "quarterly"]

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def aapl() -> sa.Stock:
    return sa.stock("AAPL")


@pytest.fixture(scope="module")
def spy() -> sa.ETF:
    return sa.etf("SPY")


# --- financials ---


@pytest.mark.parametrize("period", ["annual", "quarterly"])
def test_income_statement(aapl: sa.Stock, period: Period) -> None:
    df = aapl.financials.income_statement(period=period)
    assert isinstance(df, pd.DataFrame) and not df.empty
    assert "revenue" in df.columns


def test_balance_sheet(aapl: sa.Stock) -> None:
    df = aapl.financials.balance_sheet()
    assert isinstance(df, pd.DataFrame) and not df.empty


def test_cash_flow(aapl: sa.Stock) -> None:
    df = aapl.financials.cash_flow()
    assert isinstance(df, pd.DataFrame) and not df.empty


def test_ratios(aapl: sa.Stock) -> None:
    df = aapl.ratios()
    assert isinstance(df, pd.DataFrame) and not df.empty


# --- forecasts ---


def test_forecasts_estimates(aapl: sa.Stock) -> None:
    df = aapl.forecasts.estimates()
    assert isinstance(df, pd.DataFrame) and not df.empty
    assert "revenue" in df.columns
    assert "is_estimate" in df.columns
    assert df["is_estimate"].dtype == bool


def test_forecasts_revenue(aapl: sa.Stock) -> None:
    s = aapl.forecasts.revenue()
    assert isinstance(s, pd.Series) and not s.empty


def test_forecasts_eps(aapl: sa.Stock) -> None:
    s = aapl.forecasts.eps()
    assert isinstance(s, pd.Series) and not s.empty


def test_forecasts_price_targets(aapl: sa.Stock) -> None:
    pt = aapl.forecasts.price_targets()
    assert isinstance(pt, dict)
    assert set(pt.keys()) == {
        "high",
        "low",
        "average",
        "median",
        "current",
        "num_price_targets",
    }
    assert "avg" not in pt
    assert "source" not in pt
    assert isinstance(pt["average"], (int, float))
    assert pt["current"] is not None


def test_forecasts_recommendations(aapl: sa.Stock) -> None:
    df = aapl.forecasts.recommendations()
    assert isinstance(df, pd.DataFrame)


# --- statistics ---


def test_statistics(aapl: sa.Stock) -> None:
    df = aapl.statistics()
    assert isinstance(df, pd.DataFrame) and not df.empty
    assert set(["section", "id", "title", "value"]).issubset(df.columns)


# --- company ---


def test_company_profile(aapl: sa.Stock) -> None:
    p = aapl.company.profile()
    assert isinstance(p, dict)
    assert "name" in p and p["name"] == "Apple Inc."


def test_company_description(aapl: sa.Stock) -> None:
    d = aapl.company.description()
    assert isinstance(d, str) and len(d) > 50


def test_company_executives(aapl: sa.Stock) -> None:
    df = aapl.company.executives()
    assert isinstance(df, pd.DataFrame) and not df.empty


# --- history ---


def test_price_history(aapl: sa.Stock) -> None:
    df = aapl.history.prices()
    assert isinstance(df, pd.DataFrame) and not df.empty
    assert "close" in df.columns
    assert isinstance(df.index, pd.DatetimeIndex)


def test_price_history_adjusted_columns(aapl: sa.Stock) -> None:
    """Gap #7: prices() must include adjusted_close and dividend columns."""
    df = aapl.history.prices()
    assert "adjusted_close" in df.columns
    assert "dividend" in df.columns


def test_market_cap_history(aapl: sa.Stock) -> None:
    df = aapl.history.market_cap(frequency="annual")
    assert isinstance(df, pd.DataFrame) and not df.empty


# --- dividend ---


def test_dividend_info(aapl: sa.Stock) -> None:
    info = aapl.dividend.info()
    assert isinstance(info, str) and len(info) > 10


def test_dividend_history(aapl: sa.Stock) -> None:
    df = aapl.dividend.history()
    assert isinstance(df, pd.DataFrame) and not df.empty


# --- employees ---


def test_employees_history(aapl: sa.Stock) -> None:
    df = aapl.employees.history()
    assert isinstance(df, pd.DataFrame) and not df.empty
    assert "count" in df.columns


# --- financials.metrics ---


def test_financials_metrics(aapl: sa.Stock) -> None:
    df = aapl.financials.metrics()
    assert isinstance(df, pd.DataFrame) and not df.empty


# --- overview ---


def test_overview(aapl: sa.Stock) -> None:
    ov = aapl.overview()
    assert isinstance(ov, dict)
    assert "marketCap" in ov
    assert "description" in ov


# --- transcripts ---


def test_transcripts(aapl: sa.Stock) -> None:
    df = aapl.transcripts()
    assert isinstance(df, pd.DataFrame) and not df.empty
    assert set(["date", "quarter", "summary"]).issubset(df.columns)


def test_transcripts_no_data_returns_empty_df() -> None:
    """Bug #5: tickers without transcripts must return empty DF, not crash."""
    goog = sa.stock("GOOG")
    df = goog.transcripts()
    assert isinstance(df, pd.DataFrame)


# --- metrics (segment breakdowns) ---


def test_metrics_revenue_by_segment(aapl: sa.Stock) -> None:
    df = aapl.metrics.revenue_by_segment()
    assert isinstance(df, pd.DataFrame) and not df.empty
    assert "iPhone" in df.columns


def test_metrics_gross_profit_by_type(aapl: sa.Stock) -> None:
    df = aapl.metrics.gross_profit_by_type()
    assert isinstance(df, pd.DataFrame) and not df.empty


def test_metrics_gross_margin_by_type(aapl: sa.Stock) -> None:
    df = aapl.metrics.gross_margin_by_type()
    assert isinstance(df, pd.DataFrame) and not df.empty


def test_metrics_revenue_by_geography(aapl: sa.Stock) -> None:
    df = aapl.metrics.revenue_by_geography()
    assert isinstance(df, pd.DataFrame) and not df.empty


def test_metrics_revenue_by_geography_missing_data_returns_empty() -> None:
    """Bug #6: tickers where geography data is absent must return empty DF."""
    msft = sa.stock("MSFT")
    df = msft.metrics.revenue_by_geography()
    assert isinstance(df, pd.DataFrame)


def test_metrics_operating_expense_breakdown(aapl: sa.Stock) -> None:
    df = aapl.metrics.operating_expense_breakdown()
    assert isinstance(df, pd.DataFrame) and not df.empty


def test_metrics_operating_metrics(aapl: sa.Stock) -> None:
    df = aapl.metrics.operating_metrics()
    assert isinstance(df, pd.DataFrame) and not df.empty


# --- ETF ---


def test_etf_overview(spy: sa.ETF) -> None:
    ov = spy.overview()
    assert isinstance(ov, dict)


def test_etf_sectors(spy: sa.ETF) -> None:
    df = spy.sectors()
    assert isinstance(df, pd.DataFrame) and not df.empty
    assert list(df.columns) == ["sector", "weight"]
    assert df["weight"].dtype in (float, "float64")
    assert not df["sector"].str.startswith("$").any()


def test_etf_holdings(spy: sa.ETF) -> None:
    df = spy.holdings()
    assert isinstance(df, pd.DataFrame) and not df.empty


def test_etf_history_prices(spy: sa.ETF) -> None:
    df = spy.history.prices()
    assert isinstance(df, pd.DataFrame) and not df.empty
    assert "close" in df.columns
    assert "adjusted_close" in df.columns
    assert "dividend" in df.columns


def test_etf_performance(spy: sa.ETF) -> None:
    """Bug #1: ETF.performance() must return valid data from main page."""
    df = spy.performance()
    assert isinstance(df, pd.DataFrame) and not df.empty
    assert list(df.columns) == ["period", "return"]
    periods = df["period"].tolist()
    assert "1m" in periods
    assert "YTD" in periods
    assert "1y" in periods


# --- screener ---


def test_screener_returns_dataframe() -> None:
    """Bug #2: screener() must use correct URL and return a DataFrame."""
    df = sa.screener(sector="Technology", market_cap_min=100e9)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "symbol" in df.columns
