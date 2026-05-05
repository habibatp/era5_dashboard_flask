from __future__ import annotations

from datetime import date


def validate_date_range(
    start_date: date,
    end_date: date,
    min_available_date: date,
    max_available_date: date,
) -> None:
    if start_date > end_date:
        raise ValueError("Start date must be before or equal to end date.")

    if start_date < min_available_date:
        raise ValueError(
            f"Start date must be after {min_available_date.isoformat()}."
        )

    if end_date > max_available_date:
        raise ValueError(
            f"End date must be before {max_available_date.isoformat()}."
        )


def validate_coordinates(latitude: float, longitude: float, bbox) -> None:
    west, south, east, north = bbox

    if not (south <= latitude <= north):
        raise ValueError("Latitude is outside the allowed Morocco-Spain region.")

    if not (west <= longitude <= east):
        raise ValueError("Longitude is outside the allowed Morocco-Spain region.")


def validate_box_radius(radius: float) -> None:
    if radius <= 0:
        raise ValueError("Box radius must be positive.")

    if radius > 2:
        raise ValueError("Box radius is too large for the MVP.")