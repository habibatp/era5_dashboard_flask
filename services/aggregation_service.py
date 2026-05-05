from __future__ import annotations

import xarray as xr


def extract_nearest_point_timeseries(
    dataset: xr.Dataset,
    variable_name: str,
    latitude: float,
    longitude: float,
) -> xr.DataArray:
    lat_name = "latitude" if "latitude" in dataset.coords else "lat"
    lon_name = "longitude" if "longitude" in dataset.coords else "lon"

    return dataset[variable_name].sel(
        {lat_name: latitude, lon_name: longitude},
        method="nearest",
    )


def extract_box_mean_timeseries(
    dataset: xr.Dataset,
    variable_name: str,
    latitude: float,
    longitude: float,
    box_radius_deg: float,
) -> xr.DataArray:
    lat_name = "latitude" if "latitude" in dataset.coords else "lat"
    lon_name = "longitude" if "longitude" in dataset.coords else "lon"

    lat_min = latitude - box_radius_deg
    lat_max = latitude + box_radius_deg
    lon_min = longitude - box_radius_deg
    lon_max = longitude + box_radius_deg

    lat_values = dataset[lat_name].values
    if lat_values[0] > lat_values[-1]:
        subset = dataset.sel(
            {
                lat_name: slice(lat_max, lat_min),
                lon_name: slice(lon_min, lon_max),
            }
        )
    else:
        subset = dataset.sel(
            {
                lat_name: slice(lat_min, lat_max),
                lon_name: slice(lon_min, lon_max),
            }
        )

    return subset[variable_name].mean(dim=[lat_name, lon_name])