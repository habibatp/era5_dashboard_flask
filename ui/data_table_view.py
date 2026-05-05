from __future__ import annotations

import streamlit as st
import pandas as pd


def render_data_table(df: pd.DataFrame) -> None:
    st.subheader("Data table")
    st.dataframe(df, use_container_width=True, height=350)