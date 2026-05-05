from __future__ import annotations

import pandas as pd
import pydeck as pdk


def build_location_map(latitude: float, longitude: float, location_name: str):
    df = pd.DataFrame(
        [{"lat": latitude, "lon": longitude, "name": location_name}]
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[lon, lat]",
        get_radius=18000,
        get_fill_color=[255, 140, 0, 180],
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=latitude,
        longitude=longitude,
        zoom=5,
        pitch=0,
    )

    return pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "{name}\nLat: {lat}\nLon: {lon}"},
        map_style="mapbox://styles/mapbox/light-v9",
    )