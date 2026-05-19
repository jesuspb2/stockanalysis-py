from __future__ import annotations

from typing import Any

import pandas as pd

from stockanalysis.core.http import fetch_data_json, resolve, resolve_meta


def fetch_transcript(symbol: str, transcript_id: int | str) -> dict[str, Any]:
    """Full text and Q&A for a single earnings call transcript."""
    node_data = fetch_data_json(
        f"/stocks/{symbol.lower()}/transcripts/{transcript_id}",
        prefer_keys=("title", "body", "qa", "transcript"),
    )
    result = resolve_meta(node_data)
    # Unwrap if transcript content is nested under a "transcript" key
    if set(result.keys()) <= {"transcript", "info"} and "transcript" in result:
        inner = result["transcript"]
        if isinstance(inner, dict) and any(k in inner for k in ("title", "body", "qa")):
            return inner
    return result


def fetch_transcripts(symbol: str) -> pd.DataFrame:
    """List of earnings call transcripts with metadata and summary."""
    try:
        node_data = fetch_data_json(f"/stocks/{symbol.lower()}/transcripts")
    except ValueError:
        return pd.DataFrame()
    meta = node_data[0]
    rows = resolve(meta.get("transcripts", 0), node_data)
    if not isinstance(rows, list):
        return pd.DataFrame()
    records = []
    for t in rows:
        records.append(
            {
                "id": t.get("id"),
                "date": t.get("eventDate"),
                "quarter": t.get("quarterLabel"),
                "fiscal_year": t.get("fiscalYear"),
                "title": t.get("eventTitle"),
                "summary": t.get("summaryShort"),
                "audio_url": t.get("audioUrl"),
            }
        )
    df = pd.DataFrame(records)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df.sort_values("date", ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)
    return df
