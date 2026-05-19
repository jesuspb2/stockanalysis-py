"""Shared fixtures for unit tests (no network required)."""

from __future__ import annotations

import pytest


@pytest.fixture()
def financial_node_data() -> list:
    """Minimal node_data for a financial statement endpoint."""
    return [
        {"financialData": 1},
        {"datekey": 2, "revenue": 3, "netIncome": 4},
        ["2023-09-30", "2024-09-28"],
        [383285000000, 391035000000],
        [96995000000, 93736000000],
    ]


@pytest.fixture()
def metrics_node_data() -> list:
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
def company_node_data() -> list:
    """Minimal node_data for the company endpoint."""
    return [
        {"profile": 1, "description": 2, "executives": 3},
        {"name": 4, "sector": 5, "industry": 6},
        "Apple Inc. designs, manufactures, and markets smartphones, personal computers, and more.",
        [{"name": "Tim Cook", "title": "CEO & Director"}],
        "Apple Inc.",
        "Technology",
        "Consumer Electronics",
    ]


@pytest.fixture()
def forecast_node_data() -> list:
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
def statistics_node_data() -> list:
    """Minimal node_data for the statistics endpoint."""
    return [
        {"valuation": 1, "shares": 2},
        {"data": 3},
        {"data": 4},
        [{"id": "peRatio", "title": "P/E Ratio", "value": 29.5}],
        [{"id": "sharesOut", "title": "Shares Outstanding", "value": 15300000000}],
    ]


@pytest.fixture()
def segment_node_data() -> list:
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
