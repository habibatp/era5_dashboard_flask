from __future__ import annotations

from core.models import LocationSelection


def build_city_selection(city_name: str, cities_catalog: dict[str, tuple[float, float]]) -> LocationSelection:
    lat, lon = cities_catalog[city_name]
    return LocationSelection(
        location_type="city",
        location_name=city_name,
        latitude=lat,
        longitude=lon,
    )


def build_custom_point_selection(latitude: float, longitude: float) -> LocationSelection:
    return LocationSelection(
        location_type="custom_point",
        location_name=f"Point ({latitude:.3f}, {longitude:.3f})",
        latitude=latitude,
        longitude=longitude,
    )