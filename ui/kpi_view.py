from __future__ import annotations

import streamlit as st


def render_kpis(kpis: dict, unit: str) -> None:
    st.subheader("Key indicators")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Minimum", f"{kpis['min']:.3f} {unit}")
    col2.metric("Maximum", f"{kpis['max']:.3f} {unit}")
    col3.metric("Mean", f"{kpis['mean']:.3f} {unit}")
    col4.metric("Std", f"{kpis['std']:.3f} {unit}")
    col5.metric("Count", f"{kpis['count']}")