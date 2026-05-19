from __future__ import annotations

from typing import Any

import pandas as pd

from stockanalysis.core.http import fetch_data_json, resolve, resolve_meta


def _slug_for_id(symbol: str, transcript_id: int | str) -> str:
    """Resolve a numeric transcript id to its detailSlug via the list endpoint."""
    try:
        node_data = fetch_data_json(f"/stocks/{symbol.lower()}/transcripts")
    except ValueError:
        return str(transcript_id)
    meta = node_data[0]
    rows = resolve(meta.get("transcripts", 0), node_data)
    if not isinstance(rows, list):
        return str(transcript_id)
    needle = str(transcript_id)
    for t in rows:
        if str(t.get("id")) == needle:
            return t.get("detailSlug", needle)
    return needle


def fetch_transcript(symbol: str, transcript_id: int | str) -> dict[str, Any]:
    """Full text and Q&A for a single earnings call transcript.

    transcript_id can be the detailSlug (e.g. '548666-q2-2026') from
    transcripts() or a numeric id — numeric ids are resolved to their slug
    via the transcript list endpoint.
    """
    s = str(transcript_id)
    slug = s if "-" in s else _slug_for_id(symbol, s)

    node_data = fetch_data_json(
        f"/stocks/{symbol.lower()}/transcripts/{slug}",
        prefer_keys=("transcriptQuarter",),
    )
    meta = resolve_meta(node_data)

    tq = meta.get("transcriptQuarter", {})
    if not isinstance(tq, dict):
        return meta

    turns = tq.get("transcriptTurns", [])
    qa: list[dict[str, Any]] = []
    for turn in turns if isinstance(turns, list) else []:
        para_groups = turn.get("paragraphs", [])
        texts: list[str] = []
        for group in para_groups if isinstance(para_groups, list) else []:
            for seg in group if isinstance(group, list) else [group]:
                if isinstance(seg, dict) and "text" in seg:
                    texts.append(seg["text"])
        qa.append(
            {
                "speaker": turn.get("speakerName", ""),
                "role": turn.get("role", ""),
                "text": " ".join(texts),
            }
        )

    return {
        "title": tq.get("eventTitle", ""),
        "body": tq.get("summaryLongHtml", ""),
        "qa": qa,
    }


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
                "detail_slug": t.get("detailSlug"),
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
