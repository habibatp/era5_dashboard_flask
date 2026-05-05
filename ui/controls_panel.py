from __future__ import annotations

from datetime import date
import calendar
import streamlit as st

from core.models import UserSelection
from core.validators import (
    validate_box_radius,
    validate_coordinates,
    validate_date_range,
)


def _build_date_from_selectors(prefix: str, default_date: date, min_date: date, max_date: date) -> date:
    years = list(range(min_date.year, max_date.year + 1))
    months = list(range(1, 13))

    col_y, col_m, col_d = st.columns(3)

    with col_y:
        year = st.selectbox(
            f"{prefix} year",
            years,
            index=years.index(default_date.year),
            key=f"{prefix}_year",
        )

    with col_m:
        month = st.selectbox(
            f"{prefix} month",
            months,
            index=default_date.month - 1,
            key=f"{prefix}_month",
        )

    max_day = calendar.monthrange(year, month)[1]
    days = list(range(1, max_day + 1))

    safe_default_day = min(default_date.day, max_day)

    with col_d:
        day = st.selectbox(
            f"{prefix} day",
            days,
            index=days.index(safe_default_day),
            key=f"{prefix}_day",
        )

    return date(year, month, day)


def render_controls(settings, location):
    col1, col2, col3 = st.columns(3)

    with col1:
        var_type = st.radio("Variable type", ["surface", "pressure"], index=0)

        if var_type == "surface":
            variable = st.selectbox(
                "Variable",
                list(settings.surface_variables.keys()),
                format_func=lambda x: f"{x} — {settings.surface_variables[x]}",
            )
            pressure_level = None
        else:
            variable = st.selectbox(
                "Variable",
                list(settings.pressure_variables.keys()),
                format_func=lambda x: f"{x} — {settings.pressure_variables[x]}",
            )
            pressure_level = st.selectbox(
                "Pressure level",
                settings.pressure_levels,
                index=settings.pressure_levels.index(500),
            )

    with col2:
        st.write("### Start date")
        start_date = _build_date_from_selectors(
            prefix="start",
            default_date=date(2003, 11, 1),
            min_date=settings.min_available_date,
            max_date=settings.max_available_date,
        )

        st.write("### End date")
        end_date = _build_date_from_selectors(
            prefix="end",
            default_date=min(date(2003, 11, 30), settings.max_available_date),
            min_date=settings.min_available_date,
            max_date=settings.max_available_date,
        )

    with col3:
        aggregation = st.selectbox(
            "Aggregation",
            settings.allowed_aggregations,
            index=0,
        )

        radius = st.slider(
            "Box radius",
            min_value=0.10,
            max_value=1.00,
            value=0.25,
            step=0.05,
        )

    load_button = st.button("Load data")

    if not load_button:
        return None

    try:
        validate_date_range(
            start_date,
            end_date,
            settings.min_available_date,
            settings.max_available_date,
        )
        validate_coordinates(
            location.latitude,
            location.longitude,
            settings.region.bbox,
        )
        validate_box_radius(radius)
    except ValueError as exc:
        st.error(str(exc))
        return None

    return UserSelection(
        location=location,
        variable_type=var_type,
        variable=variable,
        pressure_level=pressure_level,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        aggregation=aggregation,
        box_radius_deg=radius,
    )