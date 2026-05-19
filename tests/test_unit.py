"""Offline unit tests — no network calls. Mock fetch_data_json at the source."""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd

import stockanalysis as sa
from stockanalysis.core.http import (
    extract_financial_df,
    resolve,
    resolve_meta,
)
from stockanalysis.data.company import Company
from stockanalysis.data.dividend import Dividend
from stockanalysis.data.forecast import Forecasts
from stockanalysis.data.metrics import Metrics, _series_list_to_df
from stockanalysis.data.statistics import Statistics


# ---------------------------------------------------------------------------
# core/http helpers
# ---------------------------------------------------------------------------


def test_resolve_int_index():
    d = ["a", "b", "c"]
    assert resolve(1, d) == "b"


def test_resolve_passthrough_string():
    d = ["a"]
    assert resolve("hello", d) == "hello"


def test_resolve_dict_recursion():
    d = [{"key": 2}, None, "resolved"]
    result = resolve(0, d)
    assert result == {"key": "resolved"}


def test_resolve_list_recursion():
    d = [[2, 3], None, "x", "y"]
    result = resolve(0, d)
    assert result == ["x", "y"]


def test_resolve_out_of_bounds():
    d = ["a"]
    assert resolve(99, d) == 99


def test_extract_financial_df(financial_node_data):
    df = extract_financial_df(financial_node_data)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.index.name == "period"
    assert "revenue" in df.columns
    assert "netIncome" in df.columns
    assert list(df.index) == ["2023-09-30", "2024-09-28"]
    assert df["revenue"].tolist() == [383285000000, 391035000000]


def test_resolve_meta(company_node_data):
    result = resolve_meta(company_node_data)
    assert isinstance(result, dict)
    assert "profile" in result
    assert "description" in result


def test_series_list_to_df():
    segments = [
        {
            "name": "iPhone",
            "values": [{"x": "2024-Q1", "y": 46e9}, {"x": "2024-Q2", "y": 39e9}],
        },
        {
            "name": "Services",
            "values": [{"x": "2024-Q1", "y": 23e9}, {"x": "2024-Q2", "y": 24e9}],
        },
    ]
    df = _series_list_to_df(segments)
    assert isinstance(df, pd.DataFrame)
    assert "iPhone" in df.columns
    assert "Services" in df.columns
    assert len(df) == 2


# ---------------------------------------------------------------------------
# Company
# ---------------------------------------------------------------------------


def test_company_profile_parsing(company_node_data):
    with patch(
        "stockanalysis.data.company.fetch_data_json", return_value=company_node_data
    ):
        c = Company("AAPL")
        profile = c.profile()
    assert isinstance(profile, dict)
    assert profile["name"] == "Apple Inc."
    assert profile["sector"] == "Technology"


def test_company_description_parsing(company_node_data):
    with patch(
        "stockanalysis.data.company.fetch_data_json", return_value=company_node_data
    ):
        c = Company("AAPL")
        desc = c.description()
    assert isinstance(desc, str)
    assert len(desc) > 20


def test_company_executives_parsing(company_node_data):
    with patch(
        "stockanalysis.data.company.fetch_data_json", return_value=company_node_data
    ):
        c = Company("AAPL")
        df = c.executives()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "name" in df.columns


# ---------------------------------------------------------------------------
# Financials
# ---------------------------------------------------------------------------


def test_income_statement_columns(financial_node_data):
    with patch(
        "stockanalysis.data.financials.fetch_data_json",
        return_value=financial_node_data,
    ):
        stock = sa.stock("AAPL")
        df = stock.financials.income_statement()
    assert isinstance(df, pd.DataFrame)
    assert "revenue" in df.columns


def test_balance_sheet_returns_dataframe(financial_node_data):
    with patch(
        "stockanalysis.data.financials.fetch_data_json",
        return_value=financial_node_data,
    ):
        stock = sa.stock("AAPL")
        df = stock.financials.balance_sheet()
    assert isinstance(df, pd.DataFrame)


# ---------------------------------------------------------------------------
# Forecasts
# ---------------------------------------------------------------------------


def test_forecasts_estimates_structure(forecast_node_data):
    with patch(
        "stockanalysis.data.forecast.fetch_data_json", return_value=forecast_node_data
    ):
        f = Forecasts("AAPL")
        df = f.estimates(period="annual")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "revenue" in df.columns
    assert "eps" in df.columns


def test_forecasts_revenue_is_series(forecast_node_data):
    with patch(
        "stockanalysis.data.forecast.fetch_data_json", return_value=forecast_node_data
    ):
        f = Forecasts("AAPL")
        s = f.revenue()
    assert isinstance(s, pd.Series)


def test_forecasts_price_targets_is_dict(forecast_node_data):
    with patch(
        "stockanalysis.data.forecast.fetch_data_json", return_value=forecast_node_data
    ):
        f = Forecasts("AAPL")
        pt = f.price_targets()
    assert isinstance(pt, dict)
    assert "high" in pt and "average" in pt


def test_forecasts_recommendations_is_dataframe(forecast_node_data):
    with patch(
        "stockanalysis.data.forecast.fetch_data_json", return_value=forecast_node_data
    ):
        f = Forecasts("AAPL")
        df = f.recommendations()
    assert isinstance(df, pd.DataFrame)


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


def test_statistics_to_dataframe(statistics_node_data):
    with patch(
        "stockanalysis.data.statistics.fetch_data_json",
        return_value=statistics_node_data,
    ):
        s = Statistics("AAPL")
        df = s.to_dataframe()
    assert isinstance(df, pd.DataFrame)
    assert set(["section", "id", "title", "value"]).issubset(df.columns)
    assert "valuation" in df["section"].values


def test_statistics_all_returns_dict(statistics_node_data):
    with patch(
        "stockanalysis.data.statistics.fetch_data_json",
        return_value=statistics_node_data,
    ):
        s = Statistics("AAPL")
        result = s.all()
    assert isinstance(result, dict)
    assert "valuation" in result


# ---------------------------------------------------------------------------
# Metrics (segment breakdowns)
# ---------------------------------------------------------------------------


def test_metrics_revenue_by_segment(segment_node_data):
    with patch(
        "stockanalysis.data.metrics.fetch_data_json", return_value=segment_node_data
    ):
        m = Metrics("AAPL")
        df = m.revenue_by_segment()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "iPhone" in df.columns


def test_metrics_operating_metrics():
    node_data = [
        {"data": 1},
        {
            "annualMetrics": 2,
        },
        [
            {
                "name": "Active Devices",
                "values": [
                    {"x": "2023-09-30", "y": 2200000000},
                    {"x": "2024-09-28", "y": 2350000000},
                ],
            }
        ],
    ]
    with patch("stockanalysis.data.metrics.fetch_data_json", return_value=node_data):
        m = Metrics("AAPL")
        df = m.operating_metrics()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


# ---------------------------------------------------------------------------
# Dividend
# ---------------------------------------------------------------------------


def test_dividend_info_empty_fallback():
    node_data = [
        {"infoBox": 1, "history": 2},
        "Dividend yield: 0.50%",
        "not-a-list",
    ]
    with patch("stockanalysis.data.dividend.fetch_data_json", return_value=node_data):
        d = Dividend("AAPL")
        info = d.info()
    assert isinstance(info, str)


def test_dividend_history_returns_empty_on_bad_data():
    node_data = [
        {"infoBox": 1, "history": 2},
        "Dividend yield: 0.50%",
        "not-a-list",
    ]
    with patch("stockanalysis.data.dividend.fetch_data_json", return_value=node_data):
        d = Dividend("AAPL")
        df = d.history()
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_dividend_history_with_data():
    node_data = [
        {"infoBox": 1, "history": 2},
        "Dividend yield: 0.50%",
        [
            {"exDate": "2024-02-09", "amount": 0.24, "type": "regular"},
            {"exDate": "2024-05-10", "amount": 0.25, "type": "regular"},
        ],
    ]
    with patch("stockanalysis.data.dividend.fetch_data_json", return_value=node_data):
        d = Dividend("AAPL")
        df = d.history()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.index.name == "ex_date"
