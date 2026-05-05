from __future__ import annotations

from pathlib import Path
from typing import Optional
import tempfile
import pandas as pd
import xarray as xr
import cdsapi
from core.exceptions import CDSDownloadError


ERA5_SINGLE_LEVEL_MAP = {
    "t2m": "2m_temperature",
    "u10": "10m_u_component_of_wind",
    "v10": "10m_v_component_of_wind",
    "msl": "mean_sea_level_pressure",
    "tp": "total_precipitation",
}

ERA5_PRESSURE_LEVEL_MAP = {
    "z": "geopotential",
    "t": "temperature",
    "u": "u_component_of_wind",
    "v": "v_component_of_wind",
    "q": "specific_humidity",
    "w": "vertical_velocity",
}


def get_cds_client(cds_url: Optional[str], cds_key: Optional[str]) -> cdsapi.Client:
    if cds_url and cds_key:
        return cdsapi.Client(url=cds_url, key=cds_key)
    return cdsapi.Client()


def download_single_level_month_chunk(
    client: cdsapi.Client,
    dataset_name: str,
    variable: str,
    year: int,
    month: int,
    days: list[int],
    bbox,
    output_file: Path,
) -> Path:
    west, south, east, north = bbox
    try:
        client.retrieve(
            dataset_name,
            {
                "product_type": "reanalysis",
                "variable": ERA5_SINGLE_LEVEL_MAP[variable],
                "year": f"{year}",
                "month": f"{month:02d}",
                "day": [f"{day:02d}" for day in days],
                "time": [f"{hour:02d}:00" for hour in range(24)],
                "data_format": "netcdf",
                "download_format": "unarchived",
                "area": [north, west, south, east],
            },
            str(output_file),
        )
        return output_file
    except Exception as exc:
        raise CDSDownloadError(f"Failed to download ERA5 single-level data: {exc}") from exc


def download_pressure_level_month_chunk(
    client: cdsapi.Client,
    dataset_name: str,
    variable: str,
    pressure_level: int,
    year: int,
    month: int,
    days: list[int],
    bbox,
    output_file: Path,
) -> Path:
    west, south, east, north = bbox
    try:
        client.retrieve(
            dataset_name,
            {
                "product_type": "reanalysis",
                "variable": ERA5_PRESSURE_LEVEL_MAP[variable],
                "pressure_level": [str(pressure_level)],
                "year": f"{year}",
                "month": f"{month:02d}",
                "day": [f"{day:02d}" for day in days],
                "time": [f"{hour:02d}:00" for hour in range(24)],
                "data_format": "netcdf",
                "download_format": "unarchived",
                "area": [north, west, south, east],
            },
            str(output_file),
        )
        return output_file
    except Exception as exc:
        raise CDSDownloadError(f"Failed to download ERA5 pressure-level data: {exc}") from exc




def fetch_era5_from_api(
    data_type,
    variable,
    start_date,
    end_date,
    lat=None,
    lon=None,
    level=None
):
    client = get_cds_client(None, None)

    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)

    days = list(range(start.day, end.day + 1))
    year = start.year
    month = start.month

    output_file = Path(tempfile.gettempdir()) / f"era5_api_{data_type}_{variable}_{year}_{month:02d}.nc"

    bbox = [
        lon - 0.25,
        lat - 0.25,
        lon + 0.25,
        lat + 0.25,
    ]

    if data_type == "surface":
        download_single_level_month_chunk(
            client=client,
            dataset_name="reanalysis-era5-single-levels",
            variable=variable,
            year=year,
            month=month,
            days=days,
            bbox=bbox,
            output_file=output_file,
        )

    else:
        download_pressure_level_month_chunk(
            client=client,
            dataset_name="reanalysis-era5-pressure-levels",
            variable=variable,
            pressure_level=level,
            year=year,
            month=month,
            days=days,
            bbox=bbox,
            output_file=output_file,
        )

    ds = xr.open_dataset(output_file)

    if "valid_time" in ds.coords:
        ds = ds.rename({"valid_time": "time"})

    ds = ds.sel(latitude=lat, longitude=lon, method="nearest")
    ds = ds.sel(time=slice(start, end))

    return ds[[variable]]