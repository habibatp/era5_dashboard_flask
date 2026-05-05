from __future__ import annotations

import pandas as pd


def maybe_convert_temperature_to_celsius(df: pd.DataFrame, variable: str) -> pd.DataFrame:
    """
    Convert Kelvin to Celsius for t2m and t for dashboard readability.
    """
    if variable in {"t2m", "t"}:
        out = df.copy()
        out["value"] = out["value"] - 273.15
        return out
    return df