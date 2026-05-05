# services/era5_timeseries_service.py

import os
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime
import pandas as pd
import xarray as xr
from services.cds_client import fetch_era5_from_api

SURFACE_LOCAL_DIR = Path(
    r"C:\Users\user\Desktop\Graphcast_Project\ERA5_surface_MA_ES_6h_1986_2026"
)

PRESSURE_LOCAL_DIR = Path(
    r"C:\Users\user\Desktop\Graphcast_Project\ERA5_pressure_full_parallel_resume_1986_2026"
)


SURFACE_INSTANT_VARS = ["t2m", "u10", "v10", "msl"]
SURFACE_ACCUM_VARS = ["tp"]


def choose_era5_strategy(start_date, end_date):
    """
    Choisit automatiquement la source et la résolution.
    """
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    delta_days = (end_date - start_date).days + 1

    if delta_days <= 31:
        return {
            "source": "api",
            "mode": "api_hourly_2h",
            "description": "API CDS ERA5 hourly, affichage chaque 2h"
        }

    elif delta_days <= 92:
        return {
            "source": "local",
            "mode": "local_6h",
            "description": "Dataset local, résolution native 6h"
        }

    elif delta_days <= 183:
        return {
            "source": "local",
            "mode": "local_12h",
            "description": "Dataset local, sous-échantillonnage 12h"
        }

    elif delta_days <= 366:
        return {
            "source": "local",
            "mode": "daily_stats",
            "description": "Statistiques journalières mean/min/max"
        }

    else:
        return {
            "source": "local",
            "mode": "monthly_stats",
            "description": "Statistiques mensuelles mean/min/max"
        }


def month_range(start_date, end_date):
    """
    Retourne la liste des couples (year, month) nécessaires.
    """
    start = pd.to_datetime(start_date).replace(day=1)
    end = pd.to_datetime(end_date).replace(day=1)

    months = pd.date_range(start=start, end=end, freq="MS")
    return [(d.year, d.month) for d in months]


def find_surface_file(year, month):
    """
    Cherche le fichier surface mensuel.
    Exemple attendu :
    era5_surface_2011_11.nc
    ou era5_surface_2011_11.zip
    """
    candidates = [
        SURFACE_LOCAL_DIR / f"era5_surface_{year}_{month:02d}.zip",
        SURFACE_LOCAL_DIR / f"era5_surface_{year}_{month:02d}.nc",
    ]

    for file in candidates:
        if file.exists():
            return file

    raise FileNotFoundError(
        f"Aucun fichier surface trouvé pour {year}-{month:02d}"
    )


def load_surface_month(year, month, variable):
    """
    Charge un mois surface.
    Chaque archive contient :
    - data_stream-oper_stepType-instant.nc : t2m, u10, v10, msl
    - data_stream-oper_stepType-accum.nc   : tp
    """

    file_path = find_surface_file(year, month)

    if variable in SURFACE_INSTANT_VARS:
        internal_name = "data_stream-oper_stepType-instant.nc"
    elif variable in SURFACE_ACCUM_VARS:
        internal_name = "data_stream-oper_stepType-accum.nc"
    else:
        raise ValueError(f"Variable surface inconnue : {variable}")

    temp_dir = tempfile.mkdtemp()

    if zipfile.is_zipfile(file_path):
        with zipfile.ZipFile(file_path, "r") as z:
            z.extractall(temp_dir)

        nc_path = Path(temp_dir) / internal_name

    else:
        nc_path = file_path

    if not nc_path.exists():
        raise FileNotFoundError(
            f"Fichier interne introuvable : {internal_name}"
        )

    ds = xr.open_dataset(nc_path)

    ds = normalize_time_coordinate(ds)

    if variable not in ds.data_vars:
        raise ValueError(
            f"La variable {variable} n'existe pas dans {nc_path}"
        )

    return ds[[variable]]


def find_pressure_files(year, month, level=None):
    if level is not None:
        block = get_pressure_block_for_level(level)
        file_path = PRESSURE_LOCAL_DIR / f"era5_pressure_{year}_{month:02d}_{block}.grib"

        if not file_path.exists():
            raise FileNotFoundError(f"Fichier pression introuvable : {file_path}")

        return [file_path]

    files = []
    for blk in range(1, 5):
        file_path = PRESSURE_LOCAL_DIR / f"era5_pressure_{year}_{month:02d}_blk{blk}.grib"
        if file_path.exists():
            files.append(file_path)

    if not files:
        raise FileNotFoundError(f"Aucun fichier pression trouvé pour {year}-{month:02d}")

    return files

def load_pressure_month(year, month, variable, level=None):
    """
    Charge les données pression depuis les fichiers GRIB.
    Nécessite cfgrib installé :
    pip install cfgrib eccodes
    """

    grib_files = find_pressure_files(year, month, level)
    datasets = []

    for grib_file in grib_files:
        ds = xr.open_dataset(
            grib_file,
            engine="cfgrib",
            backend_kwargs={
                "indexpath": "",
                "filter_by_keys": {"typeOfLevel": "isobaricInhPa"}
            }
        )

        ds = ds.drop_vars(
            ["step", "surface", "number", "expver"],
            errors="ignore"
        )

        ds = normalize_time_coordinate(ds)

        if variable not in ds.data_vars:
            continue

        ds = ds[[variable]]

        if level is not None:
            level_dim = None

            for possible_dim in ["isobaricInhPa", "level", "pressure_level"]:
                if possible_dim in ds.coords:
                    level_dim = possible_dim
                    break

            if level_dim is not None:
                ds = ds.sel({level_dim: level}, method="nearest")

        datasets.append(ds)

    if not datasets:
        raise ValueError(
            f"Variable pression {variable} introuvable pour {year}-{month:02d}"
        )

    return xr.merge(datasets, compat="override")


def load_local_era5(
    data_type,
    variable,
    start_date,
    end_date,
    lat=None,
    lon=None,
    level=None
):
    """
    Charge les données locales surface ou pression.
    """

    datasets = []

    for year, month in month_range(start_date, end_date):

        if data_type == "surface":
            ds_month = load_surface_month(year, month, variable)

        elif data_type == "pressure":
            ds_month = load_pressure_month(year, month, variable, level)

        else:
            raise ValueError("data_type doit être 'surface' ou 'pressure'")

        datasets.append(ds_month)

    ds = xr.concat(
        datasets,
        dim="time",
        coords="minimal",
        compat="override",
        join="override"
    )
    ds = ds.sortby("time")

    ds = ds.sel(
        time=slice(pd.to_datetime(start_date), pd.to_datetime(end_date))
    )

    if lat is not None and lon is not None:
        ds = ds.sel(
            latitude=lat,
            longitude=lon,
            method="nearest"
        )

    return ds

def _unit(variable: str) -> str:
    if variable in {"t2m", "t"}:
        return "°C"
    if variable in {"u10", "v10", "u", "v"}:
        return "m/s"
    if variable == "msl":
        return "hPa"
    if variable == "tp":
        return "mm"
    if variable == "q":
        return "kg/kg"
    if variable == "w":
        return "Pa/s"
    if variable == "z":
        return "m²/s²"
    return ""

def apply_visualization_strategy(ds, variable, strategy):
    """
    Applique la logique de résolution selon la période.
    """

    mode = strategy["mode"]

    if mode == "local_6h":
        return ds

    if mode == "local_12h":
        return ds.resample(time="12h").mean()

    if mode == "daily_stats":
        mean_ds = ds.resample(time="1D").mean()
        min_ds = ds.resample(time="1D").min()
        max_ds = ds.resample(time="1D").max()

        return xr.Dataset({
            f"{variable}_mean": mean_ds[variable],
            f"{variable}_min": min_ds[variable],
            f"{variable}_max": max_ds[variable],
        })

    if mode == "monthly_stats":
        mean_ds = ds.resample(time="1MS").mean()
        min_ds = ds.resample(time="1MS").min()
        max_ds = ds.resample(time="1MS").max()

        return xr.Dataset({
            f"{variable}_mean": mean_ds[variable],
            f"{variable}_min": min_ds[variable],
            f"{variable}_max": max_ds[variable],
        })

    return ds


def dataset_to_timeseries_json(ds):
    """
    Convertit xarray Dataset vers JSON simple pour Flask/frontend.
    """

    df = ds.to_dataframe().reset_index()

    # Supprimer les colonnes techniques ERA5
    df = df.drop(
        columns=[
            "latitude",
            "longitude",
            "number",
            "expver",
            "step",
            "surface",
            "heightAboveGround"
        ],
        errors="ignore"
    )

    df = df.dropna()

    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"]).dt.strftime("%Y-%m-%d %H:%M:%S")

    return df.to_dict(orient="records")


def get_era5_timeseries(
    data_type,
    variable,
    start_date,
    end_date,
    lat=None,
    lon=None,
    level=None,
    use_api_callback=None
):
    """
    Fonction principale appelée par les routes Flask.

    data_type:
        'surface' ou 'pressure'

    variable:
        surface : t2m, u10, v10, msl, tp
        pressure : z, t, u, v, q, w ...

    Pour <= 31 jours :
        utilise API CDS si use_api_callback est fourni.

    Pour > 31 jours :
        utilise dataset local.
    """

    strategy = choose_era5_strategy(start_date, end_date)

    if strategy["source"] == "api":
        ds = fetch_era5_from_api(
        data_type=data_type,
        variable=variable,
        start_date=start_date,
        end_date=end_date,
        lat=lat,
        lon=lon,
        level=level
        )

        ds = normalize_time_coordinate(ds)

        ds = ds.resample(time="2h").nearest()

    else:
        ds = load_local_era5(
            data_type=data_type,
            variable=variable,
            start_date=start_date,
            end_date=end_date,
            lat=lat,
            lon=lon,
            level=level
        )
    
        ds = convert_era5_units(ds, variable)
        ds = apply_visualization_strategy(ds, variable, strategy)


    return {
        "strategy": strategy,
        "variable": variable,
        "unit": _unit(variable),
        "data": dataset_to_timeseries_json(ds)
    }


def convert_era5_units(ds, variable):
    if variable in {"t2m", "t"}:
        ds[variable] = ds[variable] - 273.15

    elif variable == "msl":
        ds[variable] = ds[variable] / 100.0

    elif variable == "tp":
        ds[variable] = ds[variable] * 1000.0

    return ds


def normalize_time_coordinate(ds):
    if "valid_time" in ds.coords:
        if "time" in ds.coords or "time" in ds.variables:
            ds = ds.drop_vars("time", errors="ignore")

        ds = ds.rename({"valid_time": "time"})

    return ds

def get_pressure_block_for_level(level):
    level = int(level)

    level_blocks = {
        "blk1": [1, 2, 3, 5, 7, 10, 20, 30, 50],
        "blk2": [70, 100, 125, 150, 175, 200, 225, 250, 300],
        "blk3": [350, 400, 450, 500, 550, 600, 650, 700, 750],
        "blk4": [775, 800, 825, 850, 875, 900, 925, 950, 975, 1000],
    }

    for block_name, levels in level_blocks.items():
        if level in levels:
            return block_name

    raise ValueError(f"Niveau de pression non supporté : {level}")