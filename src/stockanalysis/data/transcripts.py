from __future__ import annotations

import pandas as pd

from stockanalysis.core.http import fetch_data_json, resolve


def fetch_transcripts(symbol: str) -> pd.DataFrame:
    """List of earnings call transcripts with metadata and summary."""
    node_data = fetch_data_json(f"/stocks/{symbol.lower()}/transcripts")
    meta = node_data[0]
    rows = resolve(meta["transcripts"], node_data)
    if not isinstance(rows, list):
        return pd.DataFrame()
    records = []
    for t in rows:
        records.append({
            "id": t.get("id"),
            "date": t.get("eventDate"),
            "quarter": t.get("quarterLabel"),
            "fiscal_year": t.get("fiscalYear"),
            "title": t.get("eventTitle"),
            "summary": t.get("summaryShort"),
            "audio_url": t.get("audioUrl"),
        })
    df = pd.DataFrame(records)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df.sort_values("date", ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)
    return df
