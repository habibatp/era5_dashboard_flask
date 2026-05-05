from __future__ import annotations

import streamlit as st

from plotting.kpi_plotter import compute_kpis
from plotting.timeseries_plotter import build_timeseries_figure
from services.export_service import dataframe_to_csv_bytes
from ui.data_table_view import render_data_table
from ui.kpi_view import render_kpis
from ui.map_selector import render_location_map


def render_dashboard(result, selection, settings) -> None:
    """
    Main dashboard renderer.
    """

    # --- TOP SECTION ---
    col1, col2 = st.columns([1, 2])

    with col1:
        render_location_map(
            latitude=result.latitude,
            longitude=result.longitude,
            location_name=result.location_name,
        )

        st.subheader("Selection summary")
        st.write(f"**Location:** {result.location_name}")
        st.write(f"**Variable:** {result.variable}")
        st.write(f"**Date range:** {selection.start_date} → {selection.end_date}")
        st.write(f"**Aggregation:** {result.aggregation}")
        st.write(f"**Source:** {result.source}")

    with col2:
        title = f"{result.variable} evolution — {result.location_name}"
        fig = build_timeseries_figure(
            result.dataframe,
            title=title,
            y_label=result.unit,
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- KPI ---
    kpis = compute_kpis(result.dataframe)
    render_kpis(kpis, result.unit)

    # --- DOWNLOAD ---
    st.download_button(
        label="Download CSV",
        data=dataframe_to_csv_bytes(result.dataframe),
        file_name=f"{result.variable}_{result.location_name}_{selection.start_date}_{selection.end_date}.csv".replace(" ", "_"),
        mime="text/csv",
    )

    # --- TABLE ---
    render_data_table(result.dataframe)