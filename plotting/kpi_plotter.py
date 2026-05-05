from __future__ import annotations

import pandas as pd


def compute_kpis(df: pd.DataFrame) -> dict:
    if "value" in df.columns:
        return {
            "min": float(df["value"].min()),
            "max": float(df["value"].max()),
            "mean": float(df["value"].mean()),
            "std": float(df["value"].std()) if len(df) > 1 else 0.0,
            "count": int(df["value"].count()),
        }
    else:
        return {
            "min": float(df["min"].min()),
            "max": float(df["max"].max()),
            "mean": float(df["mean"].mean()),
            "std": float(df["mean"].std()) if len(df) > 1 else 0.0,
            "count": int(df["mean"].count()),
        }