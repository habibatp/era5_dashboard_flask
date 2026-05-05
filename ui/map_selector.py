from __future__ import annotations

import streamlit as st
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium

from services.geo_service import (
    build_city_selection,
    build_custom_point_selection,
)


def render_map_selector(settings):
    """
    Render the map and allow:
    - city selection
    - manual coordinates
    - direct click on map
    """
    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("### Carte")

        m = folium.Map(
            location=[35.0, -5.0],
            zoom_start=5,
            tiles="OpenStreetMap",
            control_scale=True,
        )

        # city markers
        for city_name, (lat, lon) in settings.cities.items():
            folium.CircleMarker(
                location=[lat, lon],
                radius=5,
                color="red",
                fill=True,
                fill_color="red",
                fill_opacity=0.8,
                popup=city_name,
                tooltip=city_name,
            ).add_to(m)

        # enable rectangle drawing for future bbox support
        Draw(
            export=False,
            draw_options={
                "polyline": False,
                "polygon": False,
                "circle": False,
                "circlemarker": False,
                "marker": False,
                "rectangle": True,
            },
            edit_options={"edit": False},
        ).add_to(m)

        map_data = st_folium(
            m,
            height=500,
            use_container_width=True,
            returned_objects=["last_clicked", "all_drawings"],
        )

    with col2:
        st.write("### Sélectionnez l'emplacement")

        mode = st.radio(
            "Mode de sélection",
            ["Ville", "Coordonnées", "Clic sur la carte"],
            index=0,
        )

        if mode == "Ville":
            city = st.selectbox(
                "Ville",
                list(settings.cities.keys()),
                index=list(settings.cities.keys()).index("Marrakech")
                if "Marrakech" in settings.cities else 0,
            )
            location = build_city_selection(city, settings.cities)

        elif mode == "Coordonnées":
            lat = st.number_input("Latitude", value=31.6295, format="%.4f")
            lon = st.number_input("Longitude", value=-7.9811, format="%.4f")
            location = build_custom_point_selection(lat, lon)

        else:
            clicked = map_data.get("last_clicked") if map_data else None

            if clicked:
                lat = float(clicked["lat"])
                lon = float(clicked["lng"])
                location = build_custom_point_selection(lat, lon)
                st.success("Point récupéré depuis la carte.")
            else:
                st.info("Cliquez sur la carte pour choisir un point.")
                location = build_custom_point_selection(31.6295, -7.9811)

        st.markdown("### Zone choisie")
        st.write(f"**Nom :** {location.location_name}")
        st.write(f"**Latitude :** {location.latitude:.4f}")
        st.write(f"**Longitude :** {location.longitude:.4f}")

        drawings = map_data.get("all_drawings") if map_data else None
        if drawings:
            st.caption("Rectangle détecté sur la carte. On pourra l’utiliser pour une vraie bbox ensuite.")

    return location


def render_location_map(latitude: float, longitude: float, location_name: str) -> None:
    st.write("### Localisation sélectionnée")

    m = folium.Map(
        location=[latitude, longitude],
        zoom_start=7,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    folium.Marker(
        location=[latitude, longitude],
        popup=location_name,
        tooltip=location_name,
    ).add_to(m)

    st_folium(
        m,
        height=320,
        use_container_width=True,
        returned_objects=[],
    )