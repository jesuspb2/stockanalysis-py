"""Offline unit tests — no network calls. Mock fetch_data_json at the source."""

from __future__ import annotations

import warnings
from typing import Any
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import stockanalysis as sa
from stockanalysis.core.http import (
    extract_financial_df,
    resolve,
    resolve_meta,
)
from stockanalysis.data.company import Company
from stockanalysis.data.dividend import Dividend
from stockanalysis.data.employees import Employees
from stockanalysis.data.etf_history import ETFHistory
from stockanalysis.data.etf_overview import fetch_etf_performance
from stockanalysis.data.forecast import Forecasts
from stockanalysis.data.history import History
from stockanalysis.data.metrics import Metrics, _segment_df, _series_list_to_df
from stockanalysis.data.statistics import Statistics
from stockanalysis.data.transcripts import fetch_transcripts


# ---------------------------------------------------------------------------
# core/http helpers
# ---------------------------------------------------------------------------


def test_resolve_int_index() -> None:
    d: list[Any] = ["a", "b", "c"]
    assert resolve(1, d) == "b"


def test_resolve_passthrough_string() -> None:
    d: list[Any] = ["a"]
    assert resolve("hello", d) == "hello"


def test_resolve_dict_recursion() -> None:
    d: list[Any] = [{"key": 2}, None, "resolved"]
    result = resolve(0, d)
    assert result == {"key": "resolved"}


def test_resolve_list_recursion() -> None:
    d: list[Any] = [[2, 3], None, "x", "y"]
    result = resolve(0, d)
    assert result == ["x", "y"]


def test_resolve_out_of_bounds() -> None:
    d: list[Any] = ["a"]
    assert resolve(99, d) == 99


def test_extract_financial_df(financial_node_data: list[Any]) -> None:
    df = extract_financial_df(financial_node_data)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.index.name == "period"
    assert "revenue" in df.columns
    assert "netIncome" in df.columns
    assert list(df.index) == ["2023-09-30", "2024-09-28"]
    assert df["revenue"].tolist() == [383285000000, 391035000000]


def test_resolve_meta(company_node_data: list[Any]) -> None:
    result = resolve_meta(company_node_data)
    assert isinstance(result, dict)
    assert "profile" in result
    assert "description" in result


def test_series_list_to_df() -> None:
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
# fetch_data_json — dynamic node resolution
# ---------------------------------------------------------------------------


def test_fetch_data_json_raises_on_error_node() -> None:
    from stockanalysis.core.http import clear_cache, fetch_data_json

    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "nodes": [{"type": "error", "error": {"message": "not found"}, "status": 404}]
    }
    with patch("stockanalysis.core.http.get_session") as mock_sess:
        mock_sess.return_value.get.return_value = mock_resp
        clear_cache()
        with pytest.raises(ValueError, match="not found"):
            fetch_data_json("/test/no-data-node")


def test_fetch_data_json_raises_with_no_data_key() -> None:
    from stockanalysis.core.http import clear_cache, fetch_data_json

    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "nodes": [
            {"type": "data"},  # type is "data" but no "data" key
        ]
    }
    with patch("stockanalysis.core.http.get_session") as mock_sess:
        mock_sess.return_value.get.return_value = mock_resp
        clear_cache()
        with pytest.raises(ValueError, match="no data node found"):
            fetch_data_json("/test/no-data-key")


def test_fetch_data_json_finds_node_not_at_index_2() -> None:
    from stockanalysis.core.http import clear_cache, fetch_data_json

    expected: list[Any] = [{"key": "value"}]
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "nodes": [
            {"type": "session"},  # index 0 — no "data" key
            {"type": "data", "data": expected},  # index 1 — should be found
        ]
    }
    with patch("stockanalysis.core.http.get_session") as mock_sess:
        mock_sess.return_value.get.return_value = mock_resp
        clear_cache()
        result = fetch_data_json("/test/node-at-index-1")
    assert result == expected


# ---------------------------------------------------------------------------
# Company
# ---------------------------------------------------------------------------


def test_company_profile_parsing(company_node_data: list[Any]) -> None:
    with patch(
        "stockanalysis.data.company.fetch_data_json", return_value=company_node_data
    ):
        c = Company("AAPL")
        profile = c.profile()
    assert isinstance(profile, dict)
    assert profile["name"] == "Apple Inc."
    assert profile["sector"] == "Technology"


def test_company_description_parsing(company_node_data: list[Any]) -> None:
    with patch(
        "stockanalysis.data.company.fetch_data_json", return_value=company_node_data
    ):
        c = Company("AAPL")
        desc = c.description()
    assert isinstance(desc, str)
    assert len(desc) > 20


def test_company_executives_parsing(company_node_data: list[Any]) -> None:
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


def test_income_statement_columns(financial_node_data: list[Any]) -> None:
    with patch(
        "stockanalysis.data.financials.fetch_data_json",
        return_value=financial_node_data,
    ):
        stock = sa.stock("AAPL")
        df = stock.financials.income_statement()
    assert isinstance(df, pd.DataFrame)
    assert "revenue" in df.columns


def test_balance_sheet_returns_dataframe(financial_node_data: list[Any]) -> None:
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


def test_forecasts_estimates_structure(forecast_node_data: list[Any]) -> None:
    with patch(
        "stockanalysis.data.forecast.fetch_data_json", return_value=forecast_node_data
    ):
        f = Forecasts("AAPL")
        df = f.estimates(period="annual")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "revenue" in df.columns
    assert "eps" in df.columns


def test_forecasts_revenue_is_series(forecast_node_data: list[Any]) -> None:
    with patch(
        "stockanalysis.data.forecast.fetch_data_json", return_value=forecast_node_data
    ):
        f = Forecasts("AAPL")
        s = f.revenue()
    assert isinstance(s, pd.Series)


def test_forecasts_price_targets_is_dict(forecast_node_data: list[Any]) -> None:
    with patch(
        "stockanalysis.data.forecast.fetch_data_json", return_value=forecast_node_data
    ):
        f = Forecasts("AAPL")
        pt = f.price_targets()
    assert isinstance(pt, dict)
    assert "high" in pt and "average" in pt


def test_forecasts_recommendations_is_dataframe(forecast_node_data: list[Any]) -> None:
    with patch(
        "stockanalysis.data.forecast.fetch_data_json", return_value=forecast_node_data
    ):
        f = Forecasts("AAPL")
        df = f.recommendations()
    assert isinstance(df, pd.DataFrame)


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


def test_statistics_to_dataframe(statistics_node_data: list[Any]) -> None:
    with patch(
        "stockanalysis.data.statistics.fetch_data_json",
        return_value=statistics_node_data,
    ):
        s = Statistics("AAPL")
        df = s.to_dataframe()
    assert isinstance(df, pd.DataFrame)
    assert set(["section", "id", "title", "value"]).issubset(df.columns)
    assert "valuation" in df["section"].values


def test_statistics_all_returns_dict(statistics_node_data: list[Any]) -> None:
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


def test_metrics_revenue_by_segment(segment_node_data: list[Any]) -> None:
    with patch(
        "stockanalysis.data.metrics.fetch_data_json", return_value=segment_node_data
    ):
        m = Metrics("AAPL")
        df = m.revenue_by_segment()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "iPhone" in df.columns


def test_metrics_operating_metrics() -> None:
    node_data: list[Any] = [
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


def test_segment_df_returns_empty_when_data_key_missing() -> None:
    """Bug #6: _segment_df must not KeyError when meta has no 'data' key."""
    node_data: list[Any] = [
        {},  # meta with no "data" key
    ]
    df = _segment_df(node_data)
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_segment_df_returns_empty_when_period_missing() -> None:
    node_data: list[Any] = [
        {"data": 1},
        {"data": 2},
        {},  # no "quarterly" or "trailing" key
    ]
    df = _segment_df(node_data, period="quarterly")
    assert isinstance(df, pd.DataFrame)
    assert df.empty


# ---------------------------------------------------------------------------
# Dividend
# ---------------------------------------------------------------------------


def test_dividend_info_empty_fallback() -> None:
    node_data: list[Any] = [
        {"infoBox": 1, "history": 2},
        "Dividend yield: 0.50%",
        "not-a-list",
    ]
    with patch("stockanalysis.data.dividend.fetch_data_json", return_value=node_data):
        d = Dividend("AAPL")
        info = d.info()
    assert isinstance(info, str)


def test_dividend_history_missing_history_key() -> None:
    """Bug #1: no-dividend stocks return meta without 'history' key → must not raise."""
    node_data: list[Any] = [
        {"infoBox": 1},
        "No dividend history available.",
    ]
    with patch("stockanalysis.data.dividend.fetch_data_json", return_value=node_data):
        d = Dividend("BRK.B")
        df = d.history()
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_dividend_history_returns_empty_on_bad_data() -> None:
    node_data: list[Any] = [
        {"infoBox": 1, "history": 2},
        "Dividend yield: 0.50%",
        "not-a-list",
    ]
    with patch("stockanalysis.data.dividend.fetch_data_json", return_value=node_data):
        d = Dividend("AAPL")
        df = d.history()
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_dividend_history_with_data() -> None:
    node_data: list[Any] = [
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


# ---------------------------------------------------------------------------
# Employees — quarterly warning (Gap #8)
# ---------------------------------------------------------------------------


def test_employees_quarterly_warns_when_empty(employees_node_data: list[Any]) -> None:
    """employees.history('quarterly') must warn when no data is available."""
    with patch(
        "stockanalysis.data.employees.fetch_data_json",
        return_value=employees_node_data,
    ):
        e = Employees("AAPL")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            df = e.history(period="quarterly")
    assert isinstance(df, pd.DataFrame)
    assert df.empty
    assert any("quarterly" in str(w.message).lower() for w in caught)


def test_employees_annual_no_warning(employees_node_data: list[Any]) -> None:
    with patch(
        "stockanalysis.data.employees.fetch_data_json",
        return_value=employees_node_data,
    ):
        e = Employees("AAPL")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            df = e.history(period="annual")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert not any("quarterly" in str(w.message).lower() for w in caught)


# ---------------------------------------------------------------------------
# Transcripts — graceful error handling (Bug #5)
# ---------------------------------------------------------------------------


def test_fetch_transcripts_returns_empty_on_api_error() -> None:
    """Bug #5: fetch_transcripts must return empty DF when API returns error node."""
    with patch(
        "stockanalysis.data.transcripts.fetch_data_json",
        side_effect=ValueError("API returned no data: not found"),
    ):
        df = fetch_transcripts("GOOG")
    assert isinstance(df, pd.DataFrame)
    assert df.empty


# ---------------------------------------------------------------------------
# ETF performance — reads main page, renames columns (Bug #1)
# ---------------------------------------------------------------------------


def test_etf_performance_columns_renamed(etf_main_node_data: list[Any]) -> None:
    """Bug #1: fetch_etf_performance must use main ETF page and rename columns."""
    with patch(
        "stockanalysis.data.etf_overview.fetch_data_json",
        return_value=etf_main_node_data,
    ):
        df = fetch_etf_performance("SPY")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert list(df.columns) == ["period", "return"]
    periods = df["period"].tolist()
    assert "1m" in periods
    assert "YTD" in periods
    assert "1y" in periods
    assert "5y_cagr" in periods
    assert "10y_cagr" in periods
    assert "max_cagr" in periods


def test_etf_performance_returns_empty_when_no_performance_key() -> None:
    node_data: list[Any] = [{"description": 1}, "No performance data here."]
    with patch(
        "stockanalysis.data.etf_overview.fetch_data_json", return_value=node_data
    ):
        df = fetch_etf_performance("SPY")
    assert isinstance(df, pd.DataFrame)
    assert df.empty or list(df.columns) == ["period", "return"]


# ---------------------------------------------------------------------------
# History prices — adjusted_close and dividend columns (Gap #7)
# ---------------------------------------------------------------------------


def test_history_prices_has_adjusted_close_and_dividend(
    history_node_data: list[Any],
) -> None:
    """Gap #7: prices() must expose adjusted_close and dividend columns."""
    with patch(
        "stockanalysis.data.history.fetch_data_json", return_value=history_node_data
    ):
        h = History("AAPL")
        df = h.prices()
    assert isinstance(df, pd.DataFrame)
    assert "adjusted_close" in df.columns
    assert "dividend" in df.columns
    assert df["dividend"].iloc[1] == pytest.approx(0.24)


def test_etf_history_prices_has_adjusted_close_and_dividend(
    history_node_data: list[Any],
) -> None:
    """Gap #7: ETFHistory.prices() must also expose adjusted_close and dividend."""
    with patch(
        "stockanalysis.data.etf_history.fetch_data_json", return_value=history_node_data
    ):
        h = ETFHistory("SPY")
        df = h.prices()
    assert isinstance(df, pd.DataFrame)
    assert "adjusted_close" in df.columns
    assert "dividend" in df.columns
