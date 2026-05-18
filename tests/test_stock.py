import pandas as pd
import pytest
import stockanalysis as sa

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def aapl():
    return sa.stock("AAPL")


# --- financials ---


@pytest.mark.parametrize("period", ["annual", "quarterly"])
def test_income_statement(aapl, period):
    df = aapl.financials.income_statement(period=period)
    assert isinstance(df, pd.DataFrame) and not df.empty
    assert "revenue" in df.columns


def test_balance_sheet(aapl):
    df = aapl.financials.balance_sheet()
    assert isinstance(df, pd.DataFrame) and not df.empty


def test_cash_flow(aapl):
    df = aapl.financials.cash_flow()
    assert isinstance(df, pd.DataFrame) and not df.empty


def test_ratios(aapl):
    df = aapl.ratios()
    assert isinstance(df, pd.DataFrame) and not df.empty


# --- forecasts ---


def test_forecasts_estimates(aapl):
    df = aapl.forecasts.estimates()
    assert isinstance(df, pd.DataFrame) and not df.empty
    assert "revenue" in df.columns


def test_forecasts_revenue(aapl):
    s = aapl.forecasts.revenue()
    assert isinstance(s, pd.Series) and not s.empty


def test_forecasts_eps(aapl):
    s = aapl.forecasts.eps()
    assert isinstance(s, pd.Series) and not s.empty


def test_forecasts_price_targets(aapl):
    pt = aapl.forecasts.price_targets()
    assert isinstance(pt, dict)


def test_forecasts_recommendations(aapl):
    df = aapl.forecasts.recommendations()
    assert isinstance(df, pd.DataFrame)


# --- statistics ---


def test_statistics(aapl):
    df = aapl.statistics()
    assert isinstance(df, pd.DataFrame) and not df.empty
    assert set(["section", "id", "title", "value"]).issubset(df.columns)


# --- company ---


def test_company_profile(aapl):
    p = aapl.company.profile()
    assert isinstance(p, dict)
    assert "name" in p and p["name"] == "Apple Inc."


def test_company_description(aapl):
    d = aapl.company.description()
    assert isinstance(d, str) and len(d) > 50


def test_company_executives(aapl):
    df = aapl.company.executives()
    assert isinstance(df, pd.DataFrame) and not df.empty


# --- history ---


def test_price_history(aapl):
    df = aapl.history.prices()
    assert isinstance(df, pd.DataFrame) and not df.empty
    assert "close" in df.columns


def test_market_cap_history(aapl):
    df = aapl.history.market_cap(frequency="annual")
    assert isinstance(df, pd.DataFrame) and not df.empty


# --- dividend ---


def test_dividend_info(aapl):
    info = aapl.dividend.info()
    assert isinstance(info, str) and len(info) > 10


def test_dividend_history(aapl):
    df = aapl.dividend.history()
    assert isinstance(df, pd.DataFrame) and not df.empty


# --- employees ---


def test_employees_history(aapl):
    df = aapl.employees.history()
    assert isinstance(df, pd.DataFrame) and not df.empty
    assert "count" in df.columns


# --- financials.metrics ---


def test_financials_metrics(aapl):
    df = aapl.financials.metrics()
    assert isinstance(df, pd.DataFrame) and not df.empty


# --- overview ---


def test_overview(aapl):
    ov = aapl.overview()
    assert isinstance(ov, dict)
    assert "marketCap" in ov
    assert "description" in ov


# --- transcripts ---


def test_transcripts(aapl):
    df = aapl.transcripts()
    assert isinstance(df, pd.DataFrame) and not df.empty
    assert set(["date", "quarter", "summary"]).issubset(df.columns)


# --- metrics (segment breakdowns) ---


def test_metrics_revenue_by_segment(aapl):
    df = aapl.metrics.revenue_by_segment()
    assert isinstance(df, pd.DataFrame) and not df.empty
    assert "iPhone" in df.columns


def test_metrics_gross_profit_by_type(aapl):
    df = aapl.metrics.gross_profit_by_type()
    assert isinstance(df, pd.DataFrame) and not df.empty


def test_metrics_gross_margin_by_type(aapl):
    df = aapl.metrics.gross_margin_by_type()
    assert isinstance(df, pd.DataFrame) and not df.empty


def test_metrics_revenue_by_geography(aapl):
    df = aapl.metrics.revenue_by_geography()
    assert isinstance(df, pd.DataFrame) and not df.empty


def test_metrics_operating_expense_breakdown(aapl):
    df = aapl.metrics.operating_expense_breakdown()
    assert isinstance(df, pd.DataFrame) and not df.empty


def test_metrics_operating_metrics(aapl):
    df = aapl.metrics.operating_metrics()
    assert isinstance(df, pd.DataFrame) and not df.empty
