"""Shared fixtures for unit tests (no network required)."""

from __future__ import annotations

from typing import Any

import pytest


@pytest.fixture()
def financial_node_data() -> list[Any]:
    """Minimal node_data for a financial statement endpoint."""
    return [
        {"financialData": 1},
        {"datekey": 2, "revenue": 3, "netIncome": 4},
        ["2023-09-30", "2024-09-28"],
        [383285000000, 391035000000],
        [96995000000, 93736000000],
    ]


@pytest.fixture()
def metrics_node_data() -> list[Any]:
    """Minimal node_data for financials/metrics endpoint."""
    return [
        {"financialData": 1},
        {
            "datekey": 2,
            "categories": 3,
        },
        ["2023-09-30", "2024-09-28"],
        {"revenue": 4, "margins": 5},
        {"totalRevenue": [383285000000, 391035000000]},
        {"grossMargin": [0.441, 0.462]},
    ]


@pytest.fixture()
def company_node_data() -> list[Any]:
    """Minimal node_data for the company endpoint."""
    return [
        {"profile": 1, "description": 2, "executives": 3, "details": 4},
        {"name": 5, "sector": 6, "industry": 7},
        "Apple Inc. designs, manufactures, and markets smartphones, personal computers, and more.",
        [{"Name": "Tim Cook", "Title": "CEO & Director"}],
        {"isin": "US0378331005", "symbol": "AAPL"},
        "Apple Inc.",
        "Technology",
        "Consumer Electronics",
    ]


@pytest.fixture()
def forecast_node_data() -> list[Any]:
    """Minimal node_data for the forecast endpoint."""
    return [
        {"estimates": 1, "priceTargets": 2, "recommendations": 3},
        {
            "table": 4,
        },
        {"high": 250.0, "low": 150.0, "average": 200.0, "current": 185.0},
        [{"date": "2024-01-01", "strongBuy": 20, "buy": 10, "hold": 5}],
        {"annual": 5, "quarterly": 6},
        {"dates": 7, "revenue": 8, "eps": 9},
        {"dates": 10, "revenue": 11, "eps": 12},
        ["2024", "2025", "2026"],
        [383285000000, 400000000000, 420000000000],
        [6.11, 6.80, 7.50],
        ["2024-Q1", "2024-Q2"],
        [95000000000, 100000000000],
        [1.50, 1.65],
    ]


@pytest.fixture()
def statistics_node_data() -> list[Any]:
    """Minimal node_data for the statistics endpoint."""
    return [
        {"valuation": 1, "shares": 2},
        {"data": 3},
        {"data": 4},
        [{"id": "peRatio", "title": "P/E Ratio", "value": 29.5}],
        [{"id": "sharesOut", "title": "Shares Outstanding", "value": 15300000000}],
    ]


@pytest.fixture()
def segment_node_data() -> list[Any]:
    """Minimal node_data for a segment metrics endpoint (revenue-by-segment etc.)."""
    return [
        {"data": 1},
        {
            "data": 2,
        },
        {
            "quarterly": 3,
            "trailing": 3,
        },
        [
            {
                "name": "iPhone",
                "values": [
                    {"x": "2024-03-31", "y": 46000000000},
                    {"x": "2024-06-30", "y": 39300000000},
                ],
            },
            {
                "name": "Services",
                "values": [
                    {"x": "2024-03-31", "y": 23900000000},
                    {"x": "2024-06-30", "y": 24200000000},
                ],
            },
        ],
    ]


@pytest.fixture()
def etf_main_node_data() -> list[Any]:
    """Minimal node_data for an ETF main page (includes performance key)."""
    return [
        {
            "description": 1,
            "expenseRatio": 2,
            "performance": 3,
        },
        "SPDR S&P 500 ETF Trust tracks the S&P 500 index.",
        0.0945,
        {
            "tr1m": 4.015,
            "trYTD": 8.619,
            "tr1y": 25.736,
            "cagr5y": 13.745,
            "cagr10y": 15.563,
            "cagrMAX": 10.815,
        },
    ]


@pytest.fixture()
def etf_holdings_node_data() -> list[Any]:
    """Minimal node_data for the ETF /holdings page (sectors key)."""
    return [
        {"sectors": 1, "holdings": 2},
        [
            {"n": "Technology", "w": 34.24},
            {"n": "Financials", "w": 12.05},
            {"n": "Health Care", "w": 8.84},
        ],
        [],
    ]


@pytest.fixture()
def history_node_data() -> list[Any]:
    """Minimal node_data for a stock/ETF history endpoint with all columns."""
    return [
        {"data": 1},
        {
            "data": 2,
        },
        [
            {
                "t": "2024-01-02",
                "o": 185.0,
                "h": 186.5,
                "l": 184.0,
                "c": 185.8,
                "v": 50000000,
                "ch": 0.43,
                "a": 184.9,
                "div": 0.0,
            },
            {
                "t": "2024-02-09",
                "o": 188.0,
                "h": 189.0,
                "l": 187.0,
                "c": 188.7,
                "v": 45000000,
                "ch": 0.21,
                "a": 187.8,
                "div": 0.24,
            },
        ],
    ]


@pytest.fixture()
def employees_node_data() -> list[Any]:
    """Minimal node_data for the employees endpoint (quarterly list is empty)."""
    return [
        {"historical_annual": 1, "historical_quarterly": 2},
        [
            {"date": "2024-09-28", "count": 150000, "change": -1000},
            {"date": "2023-09-30", "count": 161000, "change": 5000},
        ],
        [],
    ]
