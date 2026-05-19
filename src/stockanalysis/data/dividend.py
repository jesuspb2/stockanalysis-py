from __future__ import annotations

from typing import Any, cast

import pandas as pd

from stockanalysis.core.http import fetch_data_json, parse_numeric, resolve


class Dividend:
    """Dividend history and summary information."""

    def __init__(self, symbol: str) -> None:
        self._symbol = symbol.lower()

    def _fetch(self) -> tuple[list[Any], dict[str, Any]]:
        node_data = fetch_data_json(f"/stocks/{self._symbol}/dividend")
        return node_data, node_data[0]

    def info(self) -> dict[str, Any]:
        """Structured summary of the current dividend.

        Keys: annual_amount, yield_pct, frequency, ex_date, pay_date,
        payout_ratio (all optional except summary), summary (prose fallback).
        """
        node_data, meta = self._fetch()
        summary = cast(str, resolve(meta["infoBox"], node_data))
        result: dict[str, Any] = {"summary": summary}

        if "infoTable" in meta:
            table = resolve(meta["infoTable"], node_data)
            if isinstance(table, dict):
                result["annual_amount"] = parse_numeric(table.get("annual", ""))
                result["yield_pct"] = parse_numeric(table.get("yield", ""))
                result["frequency"] = table.get("frequency")
                result["ex_date"] = table.get("exdiv")
                result["payout_ratio"] = parse_numeric(table.get("payoutRatio", ""))

        history_ref = meta.get("history")
        if history_ref is not None:
            rows = resolve(history_ref, node_data)
            if isinstance(rows, list) and rows and isinstance(rows[0], dict):
                result["pay_date"] = rows[0].get("pay")

        return result

    def history(self) -> pd.DataFrame:
        """
        Full dividend payment history.

        Returns a DataFrame indexed by ex-dividend date with columns:
        amount, type, declaration date, record date, payment date.
        """
        node_data, meta = self._fetch()
        history_ref = meta.get("history")
        if history_ref is None:
            return pd.DataFrame()
        rows = resolve(history_ref, node_data)

        if not isinstance(rows, list):
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        df = df.rename(
            columns={"dt": "date", "amt": "amount", "dec": "declaration_date"}
        )
        if "amount" in df.columns:
            df["amount"] = df["amount"].map(parse_numeric)
        date_col = next(
            (c for c in ("exDate", "ex_date", "date") if c in df.columns), None
        )
        if date_col:
            df = df.set_index(date_col)
            df.index.name = "ex_date"
        return df
