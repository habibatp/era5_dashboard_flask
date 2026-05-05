from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass(frozen=True)
class LocationSelection:
    location_type: str
    location_name: str
    latitude: float
    longitude: float


@dataclass(frozen=True)
class UserSelection:
    location: LocationSelection
    variable_type: str
    variable: str
    pressure_level: Optional[int]
    start_date: str
    end_date: str
    aggregation: str
    box_radius_deg: float


@dataclass
class TimeSeriesResult:
    dataframe: pd.DataFrame
    variable: str
    unit: str
    source: str
    latitude: float
    longitude: float
    location_name: str
    aggregation: str