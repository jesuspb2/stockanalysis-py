"""Offline unit tests — no network calls. Mock fetch_data_json at the source."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import stockanalysis as sa
from stockanalysis.core.http import (
    extract_financial_df,
    parse_numeric,
    resolve,
    resolve_meta,
)
from stockanalysis.data.company import Company
from stockanalysis.data.dividend import Dividend
from stockanalysis.data.employees import Employees
from stockanalysis.data.etf_history import ETFHistory
from stockanalysis.data.etf_overview import (
    fetch_etf_overview,
    fetch_etf_performance,
    fetch_etf_sectors,
)
from stockanalysis.data.overview import fetch_overview
from stockanalysis.data.forecast import Forecasts
from stockanalysis.data.history import History
from stockanalysis.data.metrics import Metrics, _segment_df, _series_list_to_df
from stockanalysis.data.statistics import Statistics
from stockanalysis.data.transcripts import fetch_transcript, fetch_transcripts


# ---------------------------------------------------------------------------
# core/http helpers
# ---------------------------------------------------------------------------


def test_parse_numeric_trillion() -> None:
    assert parse_numeric("4.37T") == pytest.approx(4.37e12)


def test_parse_numeric_billion_with_dollar() -> None:
    assert parse_numeric("$766.97B") == pytest.approx(766.97e9)


def test_parse_numeric_percent() -> None:
    assert parse_numeric("0.09%") == pytest.approx(0.09)


def test_parse_numeric_plain_float() -> None:
    assert parse_numeric("36.11") == pytest.approx(36.11)


def test_parse_numeric_passthrough_compound_string() -> None:
    assert parse_numeric("$1.04 (0.35%)") == "$1.04 (0.35%)"


def test_parse_numeric_passthrough_non_string() -> None:
    assert parse_numeric(42) == 42
    assert parse_numeric(3.14) == 3.14
    assert parse_numeric(None) is None


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
    """D6: executives() normalizes Title-cased API columns to snake_case."""
    with patch(
        "stockanalysis.data.company.fetch_data_json", return_value=company_node_data
    ):
        c = Company("AAPL")
        df = c.executives()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "name" in df.columns
    assert "title" in df.columns
    assert "Name" not in df.columns
    assert "Title" not in df.columns


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


def test_forecasts_recommendations_drops_noisy_columns() -> None:
    """C3: recommendations() must drop filtered/month/updated columns."""
    node_data: list[Any] = [
        {"estimates": 1, "priceTargets": 2, "recommendations": 3},
        {"table": 4},
        {"high": 250.0, "low": 150.0, "average": 200.0, "current": 185.0},
        [
            {
                "date": "2024-01-01",
                "strongBuy": 20,
                "buy": 10,
                "hold": 5,
                "sell": 1,
                "strongSell": 0,
                "month": "Jan '24",
                "updated": "2024-01-15",
                "filtered": "{'1': {'buy': 0, 'hold': 1}}",
            }
        ],
        {"annual": 5},
        {"dates": [], "revenue": [], "eps": []},
    ]
    with patch("stockanalysis.data.forecast.fetch_data_json", return_value=node_data):
        df = Forecasts("AAPL").recommendations()
    assert "filtered" not in df.columns
    assert "month" not in df.columns
    assert "updated" not in df.columns
    assert "strongBuy" in df.columns
    assert df.index.name == "date"


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


def test_segment_df_annual_aliases_trailing(
    segment_node_data: list[Any],
) -> None:
    df_trailing = _segment_df(segment_node_data, period="trailing")
    df_annual = _segment_df(segment_node_data, period="annual")
    assert not df_annual.empty
    assert df_annual.equals(df_trailing)


# ---------------------------------------------------------------------------
# Dividend
# ---------------------------------------------------------------------------


def test_dividend_info_returns_dict_with_summary() -> None:
    """D5: info() must return a dict; summary key holds the original prose."""
    node_data: list[Any] = [
        {"infoBox": 1, "history": 2},
        "Dividend yield: 0.50%",
        "not-a-list",
    ]
    with patch("stockanalysis.data.dividend.fetch_data_json", return_value=node_data):
        d = Dividend("AAPL")
        info = d.info()
    assert isinstance(info, dict)
    assert info["summary"] == "Dividend yield: 0.50%"
    assert "annual_amount" not in info  # no infoTable in fixture


def test_dividend_info_structured_fields() -> None:
    """D5: info() extracts annual_amount, yield_pct, frequency, ex_date, pay_date."""
    node_data: list[Any] = [
        {"infoBox": 1, "infoTable": 2, "history": 3},
        "Apple has an annual dividend of $1.04 per share, with a yield of 0.35%.",
        {
            "annual": 4,
            "yield": 5,
            "frequency": 6,
            "exdiv": 7,
            "payoutRatio": 8,
        },
        [{"dt": "2026-05-11", "amt": "$0.270", "pay": "2026-05-14"}],
        "$1.04",
        "0.35%",
        "Quarterly",
        "May 11, 2026",
        "12.73%",
    ]
    with patch("stockanalysis.data.dividend.fetch_data_json", return_value=node_data):
        d = Dividend("AAPL")
        info = d.info()
    assert isinstance(info, dict)
    assert info["annual_amount"] == pytest.approx(1.04)
    assert info["yield_pct"] == pytest.approx(0.35)
    assert info["frequency"] == "Quarterly"
    assert info["ex_date"] == "May 11, 2026"
    assert info["payout_ratio"] == pytest.approx(12.73)
    assert info["pay_date"] == "2026-05-14"
    assert "summary" in info


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
# Employees — annual-only API (Gap #2)
# ---------------------------------------------------------------------------


def test_employees_history_returns_annual_data(employees_node_data: list[Any]) -> None:
    """employees.history() returns annual headcount data without a period argument."""
    with patch(
        "stockanalysis.data.employees.fetch_data_json",
        return_value=employees_node_data,
    ):
        e = Employees("AAPL")
        df = e.history()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.index.name == "date"


def test_employees_history_drops_dead_columns(employees_node_data: list[Any]) -> None:
    """D4: fullTime and partTime are always None — must not appear in result."""
    node_data_with_dead_cols = [
        {"historical_annual": 1, "historical_quarterly": 2},
        [
            {
                "date": "2024-09-28",
                "count": 150000,
                "change": -1000,
                "fullTime": None,
                "partTime": None,
            },
        ],
        [],
    ]
    with patch(
        "stockanalysis.data.employees.fetch_data_json",
        return_value=node_data_with_dead_cols,
    ):
        e = Employees("AAPL")
        df = e.history()
    assert "fullTime" not in df.columns
    assert "partTime" not in df.columns


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
# ETF sectors — reads holdings page, returns clean sector/weight DataFrame (Bug B2)
# ---------------------------------------------------------------------------


def test_etf_sectors_columns_and_types(etf_holdings_node_data: list[Any]) -> None:
    """B2: fetch_etf_sectors must return sector/weight from the /holdings endpoint."""
    with patch(
        "stockanalysis.data.etf_overview.fetch_data_json",
        return_value=etf_holdings_node_data,
    ):
        df = fetch_etf_sectors("SPY")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert list(df.columns) == ["sector", "weight"]
    assert df["sector"].tolist() == ["Technology", "Financials", "Health Care"]
    assert df["weight"].tolist() == [34.24, 12.05, 8.84]


def test_etf_sectors_returns_empty_when_no_sectors_key() -> None:
    node_data: list[Any] = [{"holdings": 1}, []]
    with patch(
        "stockanalysis.data.etf_overview.fetch_data_json", return_value=node_data
    ):
        df = fetch_etf_sectors("SPY")
    assert isinstance(df, pd.DataFrame)
    assert df.empty
    assert list(df.columns) == ["sector", "weight"]


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


# ---------------------------------------------------------------------------
# B1: fetch_transcript — picks transcript node, not stock-layout node
# ---------------------------------------------------------------------------


def test_fetch_transcript_prefer_keys_picks_transcript_node() -> None:
    """B1: prefer_keys must select the transcriptQuarter node, not the layout node."""
    from stockanalysis.core.http import clear_cache, fetch_data_json

    transcript_node_data: list[Any] = [
        {"transcriptQuarter": 1, "transcriptMeta": 2},
        {
            "id": 123,
            "eventTitle": "Q1 2024",
            "summaryLongHtml": "...",
            "transcriptTurns": [],
        },
        {"title": "Q1 2024 Transcript", "description": "..."},
    ]
    layout_node_data: list[Any] = [{"info": 1}, {"type": "stock", "symbol": "AAPL"}]

    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "nodes": [
            {"type": "data", "data": transcript_node_data},  # page data — first
            {"type": "data", "data": layout_node_data},  # layout data — last
        ]
    }
    with patch("stockanalysis.core.http.get_session") as mock_sess:
        mock_sess.return_value.get.return_value = mock_resp
        clear_cache()
        result = fetch_data_json(
            "/stocks/aapl/transcripts/548666-q1-2024",
            prefer_keys=("transcriptQuarter",),
        )

    assert result is transcript_node_data
    assert "transcriptQuarter" in result[0]


def test_fetch_transcript_returns_title_body_qa() -> None:
    """B1: fetch_transcript must return a dict with title, body, qa keys."""
    transcript_node_data: list[Any] = [
        {"transcriptQuarter": 1, "transcriptMeta": 2},
        {
            "id": 12345,
            "eventTitle": "Q1 2024 Earnings Call",
            "summaryLongHtml": "<p>CEO: Revenue was strong this quarter...</p>",
            "transcriptTurns": [
                {
                    "speakerName": "Analyst",
                    "role": "Analyst",
                    "paragraphs": [
                        [{"text": "What is the outlook?", "startSec": 0, "endSec": 5}]
                    ],
                }
            ],
        },
        {"title": "Apple Q1 2024 Earnings Call Transcript", "description": "..."},
    ]
    with patch(
        "stockanalysis.data.transcripts.fetch_data_json",
        return_value=transcript_node_data,
    ):
        result = fetch_transcript("AAPL", "548666-q1-2024")

    assert isinstance(result, dict)
    assert result.get("title") == "Q1 2024 Earnings Call"
    assert "body" in result
    assert "qa" in result
    assert isinstance(result["qa"], list)
    assert result["qa"][0]["speaker"] == "Analyst"


# ---------------------------------------------------------------------------
# C2: Cryptic column name renames
# ---------------------------------------------------------------------------


def test_market_cap_renames_cryptic_columns() -> None:
    """C2: market_cap() must rename d/p/v to date/percent_change/value."""
    from stockanalysis.data.history import History

    node_data: list[Any] = [
        {"tables": 1},
        {"annual": 2},
        [
            {"d": "2023-09-30", "p": 5.12, "v": 2750000000000},
            {"d": "2024-09-28", "p": 12.34, "v": 3500000000000},
        ],
    ]
    with patch("stockanalysis.data.history.fetch_data_json", return_value=node_data):
        df = History("AAPL").market_cap()
    assert "percent_change" in df.columns
    assert "value" in df.columns
    assert df.index.name == "date"
    assert "d" not in df.columns
    assert "p" not in df.columns
    assert "v" not in df.columns


def test_etf_holdings_renames_cryptic_columns() -> None:
    """C2/D7: holdings() renames columns and strips $ prefix from symbol."""
    from stockanalysis.data.etf_holdings import ETFHoldings

    node_data: list[Any] = [
        {"holdings": 1},
        [
            {"no": 1, "n": "Apple Inc.", "s": "$AAPL", "as": "7.20%", "sh": 900000000},
            {"no": 2, "n": "Microsoft", "s": "$MSFT", "as": "6.80%", "sh": 800000000},
        ],
    ]
    with patch(
        "stockanalysis.data.etf_holdings.fetch_data_json", return_value=node_data
    ):
        df = ETFHoldings("SPY")()
    assert list(df.columns) == ["rank", "name", "symbol", "weight_pct", "shares"]
    assert "as" not in df.columns
    assert df["weight_pct"].iloc[0] == pytest.approx(7.20)
    assert df["symbol"].iloc[0] == "AAPL"
    assert df["symbol"].iloc[1] == "MSFT"


def test_dividend_history_renames_cryptic_columns() -> None:
    """C2: dividend history() must rename dt/amt/dec to date/amount/declaration_date."""
    node_data: list[Any] = [
        {"infoBox": 1, "history": 2},
        "Dividend yield: 0.50%",
        [
            {"dt": "2024-02-09", "amt": "0.24", "dec": "2024-01-25", "type": "regular"},
            {"dt": "2024-05-10", "amt": "0.25", "dec": "2024-04-26", "type": "regular"},
        ],
    ]
    with patch("stockanalysis.data.dividend.fetch_data_json", return_value=node_data):
        d = Dividend("AAPL")
        df = d.history()
    assert "amount" in df.columns
    assert "declaration_date" in df.columns
    assert "amt" not in df.columns
    assert "dec" not in df.columns
    assert df["amount"].iloc[0] == pytest.approx(0.24)


def test_income_statement_renames_cryptic_columns() -> None:
    """C2: income_statement() must rename cor/sgna/rnd to full descriptive names."""
    node_data: list[Any] = [
        {"financialData": 1},
        {"datekey": 2, "revenue": 3, "cor": 4, "sgna": 5, "rnd": 6},
        ["2023-09-30", "2024-09-28"],
        [383285000000, 391035000000],
        [210352000000, 210352000000],
        [25010000000, 26000000000],
        [29915000000, 31370000000],
    ]
    with patch("stockanalysis.data.financials.fetch_data_json", return_value=node_data):
        df = sa.stock("AAPL").financials.income_statement()
    assert "cost_of_revenue" in df.columns
    assert "sga_expense" in df.columns
    assert "rd_expense" in df.columns
    assert "cor" not in df.columns
    assert "sgna" not in df.columns
    assert "rnd" not in df.columns


def test_fetch_transcript_resolves_numeric_id_via_list() -> None:
    """B1: fetch_transcript resolves a numeric id to detailSlug via the transcript list."""
    list_node_data: list[Any] = [
        {"transcripts": 1},
        [{"id": 99999, "detailSlug": "548666-q2-2024", "quartrEventId": 548666}],
    ]
    transcript_node_data: list[Any] = [
        {"transcriptQuarter": 1, "transcriptMeta": 2},
        {
            "id": 99999,
            "eventTitle": "Q2 2024",
            "summaryLongHtml": "Prepared remarks...",
            "transcriptTurns": [],
        },
        {"title": "Apple Q2 2024", "description": "..."},
    ]

    def side_effect(path: str, **kwargs: Any) -> list[Any]:
        if "548666" in path:
            return transcript_node_data
        return list_node_data

    with patch(
        "stockanalysis.data.transcripts.fetch_data_json",
        side_effect=side_effect,
    ):
        result = fetch_transcript("AAPL", 99999)

    assert isinstance(result, dict)
    assert result.get("title") == "Q2 2024"
    assert "body" in result
    assert "qa" in result


# ---------------------------------------------------------------------------
# Dead fields — D4
# ---------------------------------------------------------------------------


def test_overview_excludes_info_table() -> None:
    """D4: infoTable always returns {} — must not appear in overview() result."""
    node_data: list[Any] = [
        {
            "marketCap": 1,
            "description": 2,
            "infoTable": 3,
        },
        3_000_000_000_000,
        "Apple Inc.",
        [],
    ]
    with patch(
        "stockanalysis.data.overview.fetch_data_json",
        return_value=node_data,
    ):
        result = fetch_overview("AAPL")
    assert "infoTable" not in result
    assert result["marketCap"] == 3_000_000_000_000


def test_screener_sector_filter_returns_matching_rows() -> None:
    """D8: screener(sector=...) must expose a sector column and filter results to that sector."""
    from stockanalysis.data.search import screener

    node_data: list[Any] = [
        {"data": 1},
        [
            {
                "s": "NVDA",
                "n": "NVIDIA Corporation",
                "marketCap": 5345469917158,
                "price": 220.7,
                "change": -0.73,
                "sector": "Technology",
                "volume": 62644556,
                "peRatio": 45.37,
            },
            {
                "s": "JPM",
                "n": "JPMorgan Chase & Co.",
                "marketCap": 700000000000,
                "price": 200.0,
                "change": 0.5,
                "sector": "Financials",
                "volume": 10000000,
                "peRatio": 12.0,
            },
        ],
    ]
    with patch("stockanalysis.data.search.fetch_data_json", return_value=node_data):
        df = screener(sector="Technology")
    assert "sector" in df.columns
    assert len(df) == 1
    assert df["sector"].iloc[0] == "Technology"
    assert df["symbol"].iloc[0] == "NVDA"


def test_etf_overview_excludes_info_table() -> None:
    """D4: infoTable always returns {} — must not appear in etf.overview() result."""
    node_data: list[Any] = [
        {
            "description": 1,
            "aum": 2,
            "infoTable": 3,
        },
        "SPDR S&P 500 ETF Trust",
        500_000_000_000,
        [],
    ]
    with patch(
        "stockanalysis.data.etf_overview.fetch_data_json",
        return_value=node_data,
    ):
        result = fetch_etf_overview("SPY")
    assert "infoTable" not in result
    assert result["aum"] == 500_000_000_000
