from __future__ import annotations

SURFACE_VARIABLE_UNITS = {
    "t2m": "K",
    "u10": "m/s",
    "v10": "m/s",
    "msl": "Pa",
    "tp": "m",
}

PRESSURE_VARIABLE_UNITS = {
    "z": "m²/s²",
    "t": "K",
    "u": "m/s",
    "v": "m/s",
    "q": "kg/kg",
    "w": "Pa/s",
}

VARIABLE_FRIENDLY_NAMES = {
    "t2m": "2m Temperature",
    "u10": "10m U Wind",
    "v10": "10m V Wind",
    "msl": "Mean Sea Level Pressure",
    "tp": "Total Precipitation",
    "z": "Geopotential",
    "t": "Temperature",
    "u": "U Wind",
    "v": "V Wind",
    "q": "Specific Humidity",
    "w": "Vertical Velocity",
}

DEFAULT_BOX_RADIUS_DEG = 0.25