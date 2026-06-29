from __future__ import annotations

import pandas as pd
from stockanalysis.core.http import fetch_data_json, resolve

_CATEGORY_PATHS: dict[str, str] = {
    "markets": "/news",
    "all-stocks": "/news/all-stocks",
    "press-releases": "/news/press-releases",
}


def fetch_market_news(category: str = "markets") -> pd.DataFrame:
    """General stock market news.

    Args:
        category: one of "markets" (default), "all-stocks", "press-releases".

    Returns a DataFrame with columns:
        time, ago, title, text, source, type, tickers, url, img
    sorted by time descending.
    """
    path = _CATEGORY_PATHS.get(category)
    if path is None:
        raise ValueError(
            f"Unknown category {category!r}. "
            f"Valid options: {list(_CATEGORY_PATHS)}"
        )

    node_data = fetch_data_json(path)
    meta = node_data[0]

    articles = resolve(meta.get("data"), node_data)
    if not isinstance(articles, list):
        return pd.DataFrame()

    records = []
    for a in articles:
        if not isinstance(a, dict):
            continue
        tickers = a.get("tickers")
        records.append(
            {
                "time": a.get("time"),
                "ago": a.get("ago"),
                "title": a.get("title"),
                "text": a.get("text"),
                "source": a.get("source"),
                "type": a.get("type"),
                "tickers": tickers if isinstance(tickers, list) else None,
                "url": a.get("url"),
                "img": a.get("img"),
            }
        )

    df = pd.DataFrame(records)
    if "time" in df.columns:
        cleaned = df["time"].str.replace(r"\s+[A-Z]{2,4}$", "", regex=True)
        df["time"] = pd.to_datetime(
            cleaned, format="%b %d, %Y, %I:%M %p", errors="coerce"
        )
        df.sort_values("time", ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)
    return df


def fetch_news(symbol: str) -> pd.DataFrame:
    """Recent news articles for a stock ticker.

    Returns a DataFrame with columns:
        time, title, text, source, type, url, img
    sorted by time descending.
    """
    node_data = fetch_data_json(f"/stocks/{symbol.lower()}")
    meta = node_data[0]

    if "news" not in meta:
        return pd.DataFrame()

    news_val = resolve(meta["news"], node_data)
    if not isinstance(news_val, dict):
        return pd.DataFrame()

    articles = news_val.get("data", [])
    if not isinstance(articles, list):
        return pd.DataFrame()

    records = []
    for a in articles:
        if not isinstance(a, dict):
            continue
        tickers = a.get("tickers")
        records.append(
            {
                "time": a.get("time"),
                "ago": a.get("ago"),
                "title": a.get("title"),
                "text": a.get("text"),
                "source": a.get("source"),
                "type": a.get("type"),
                "tickers": tickers if isinstance(tickers, list) else None,
                "url": a.get("url"),
                "img": a.get("img"),
            }
        )

    df = pd.DataFrame(records)
    if "time" in df.columns:
        # Strip trailing timezone abbreviation e.g. "Jun 8, 2026, 2:51 PM EDT"
        cleaned = df["time"].str.replace(r"\s+[A-Z]{2,4}$", "", regex=True)
        df["time"] = pd.to_datetime(
            cleaned, format="%b %d, %Y, %I:%M %p", errors="coerce"
        )
        df.sort_values("time", ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)
    return df
