from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple
from datetime import date
import os

from dotenv import load_dotenv

load_dotenv()

SURFACE_VARIABLES = {
    "t2m": "Temperature 2m",
    "u10": "Wind U 10m",
    "v10": "Wind V 10m",
    "msl": "Mean Sea Level Pressure",
    "tp": "Total Precipitation"
}

PRESSURE_VARIABLES = {
    "z": "Geopotential",
    "t": "Temperature",
    "u": "U wind",
    "v": "V wind",
    "q": "Humidity",
    "w": "Vertical velocity"
}
@dataclass(frozen=True)
class RegionConfig:
    name: str
    bbox: Tuple[float, float, float, float]


@dataclass(frozen=True)
class CacheConfig:
    cache_dir: Path
    temp_dir: Path
    max_size_gb: float


@dataclass(frozen=True)
class CDSConfig:
    url: str | None
    key: str | None
    single_dataset: str
    pressure_dataset: str


@dataclass(frozen=True)
class AppConfig:
    app_name: str
    region: RegionConfig
    cache: CacheConfig
    cds: CDSConfig
    cities: Dict[str, Tuple[float, float]]
    surface_variables: Dict[str, str]
    pressure_variables: Dict[str, str]
    pressure_levels: list[int]
    default_variable: str
    allowed_aggregations: list[str]
    min_available_date: date
    max_available_date: date


def _env_path(name: str, default: str) -> Path:
    return Path(os.getenv(name, default)).resolve()


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def get_city_catalog() -> Dict[str, Tuple[float, float]]:
    return {
        "Marrakech": (31.6295, -7.9811),
        "Casablanca": (33.5731, -7.5898),
        "Rabat": (34.0209, -6.8416),
        "Agadir": (30.4278, -9.5981),
        "Fes": (34.0331, -5.0003),
        "Tangier": (35.7595, -5.8340),
        "Madrid": (40.4168, -3.7038),
        "Barcelona": (41.3874, 2.1686),
        "Seville": (37.3891, -5.9845),
        "Malaga": (36.7213, -4.4214),
        "Granada": (37.1773, -3.5986),
    }


def get_surface_variables() -> Dict[str, str]:
    return {
        "t2m": "2m Temperature",
        "u10": "10m U Wind",
        "v10": "10m V Wind",
        "msl": "Mean Sea Level Pressure",
        "tp": "Total Precipitation",
    }


def get_pressure_variables() -> Dict[str, str]:
    return {
        "z": "Geopotential",
        "t": "Temperature",
        "u": "U Wind",
        "v": "V Wind",
        "q": "Specific Humidity",
        "w": "Vertical Velocity",
    }


def get_graphcast_pressure_levels() -> list[int]:
    return [
        1, 2, 3, 5, 7, 10, 20, 30, 50, 70,
        100, 125, 150, 175, 200, 225, 250, 300,
        350, 400, 450, 500, 550, 600, 650, 700, 750,
        775, 800, 825, 850, 875, 900, 925, 950, 975, 1000,
    ]


def load_settings() -> AppConfig:
    west = float(os.getenv("DEFAULT_BBOX_WEST", "-11"))
    south = float(os.getenv("DEFAULT_BBOX_SOUTH", "27"))
    east = float(os.getenv("DEFAULT_BBOX_EAST", "5"))
    north = float(os.getenv("DEFAULT_BBOX_NORTH", "45"))

    return AppConfig(
        app_name="ERA5 Time Series Dashboard",
        region=RegionConfig(
            name="Morocco-Spain-Alboran",
            bbox=(west, south, east, north),
        ),
        cache=CacheConfig(
            cache_dir=_env_path("CACHE_DIR", "cache_data"),
            temp_dir=_env_path("TEMP_DIR", "temp_downloads"),
            max_size_gb=_env_float("CACHE_MAX_SIZE_GB", 1.0),
        ),
        cds=CDSConfig(
            url=os.getenv("CDSAPI_URL"),
            key=os.getenv("CDSAPI_KEY"),
            single_dataset="reanalysis-era5-single-levels",
            pressure_dataset="reanalysis-era5-pressure-levels",
        ),
        cities=get_city_catalog(),
        surface_variables=get_surface_variables(),
        pressure_variables=get_pressure_variables(),
        pressure_levels=get_graphcast_pressure_levels(),
        default_variable="t2m",
        allowed_aggregations=["nearest_point", "box_mean"],
        min_available_date=date(1940, 1, 1),
        max_available_date=date.today(),
    )


def ensure_directories_exist(settings: AppConfig) -> None:
    settings.cache.cache_dir.mkdir(parents=True, exist_ok=True)
    settings.cache.temp_dir.mkdir(parents=True, exist_ok=True)